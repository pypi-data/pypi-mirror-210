# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Zoom line search algorithm."""

# Original code by Joshua George Albert:
# https://github.com/google/jax/pull/3101

from typing import Any, NamedTuple, Optional, Union
from functools import partial

#from jax._src.numpy.util import _promote_dtypes_inexact
import jax.numpy as jnp
import jax
from jax import lax
from jaxopt.tree_util import tree_vdot, tree_add_scalar_mul, tree_map
from jaxopt._src.tree_util import tree_single_dtype

_dot = partial(jnp.dot, precision=lax.Precision.HIGHEST)


def _cubicmin(a, fa, fpa, b, fb, c, fc):
  C = fpa
  db = b - a
  dc = c - a
  denom = (db * dc) ** 2 * (db - dc)
  d1 = jnp.array([[dc ** 2, -db ** 2],
                  [-dc ** 3, db ** 3]])
  A, B = _dot(d1, jnp.array([fb - fa - C * db, fc - fa - C * dc])) / denom

  radical = B * B - 3. * A * C
  xmin = a + (-B + jnp.sqrt(radical)) / (3. * A)

  return xmin


def _quadmin(a, fa, fpa, b, fb):
  D = fa
  C = fpa
  db = b - a
  B = (fb - D - C * db) / (db ** 2)
  xmin = a - C / (2. * B)
  return xmin


def _binary_replace(replace_bit, original_dict, new_dict, keys=None):
  if keys is None:
    keys = new_dict.keys()
  out = dict()
  for key in keys:
    #out[key] = jnp.where(replace_bit, new_dict[key], original_dict[key])
    out[key] = tree_map(lambda x, y: jnp.where(replace_bit, x, y),
                        new_dict[key],
                        original_dict[key])
  return out


class _ZoomState(NamedTuple):
  done: Union[bool, jnp.ndarray]
  failed: Union[bool, jnp.ndarray]
  j: Union[int, jnp.ndarray]
  a_lo: Union[float, jnp.ndarray]
  phi_lo: Union[float, jnp.ndarray]
  dphi_lo: Union[float, jnp.ndarray]
  a_hi: Union[float, jnp.ndarray]
  phi_hi: Union[float, jnp.ndarray]
  dphi_hi: Union[float, jnp.ndarray]
  a_rec: Union[float, jnp.ndarray]
  phi_rec: Union[float, jnp.ndarray]
  a_star: Union[float, jnp.ndarray]
  phi_star: Union[float, jnp.ndarray]
  dphi_star: Union[float, jnp.ndarray]
  g_star: Union[float, jnp.ndarray]
  nfev: Union[int, jnp.ndarray]
  ngev: Union[int, jnp.ndarray]
  aux_lo: Union[float, jnp.ndarray]
  aux_hi: Union[float, jnp.ndarray]
  aux_star: Union[float, jnp.ndarray]


def _zoom(restricted_func_and_grad, wolfe_one, wolfe_two, a_lo, phi_lo,
          dphi_lo, a_hi, phi_hi, dphi_hi, g_0, pass_through, has_aux=False, aux=jnp.nan):
  """
  Implementation of zoom. Algorithm 3.6 from Wright and Nocedal, 'Numerical
  Optimization', 1999, pg. 59-61. Tries cubic, quadratic, and bisection methods
  of zooming.
  """
  init_state = _ZoomState(
      done=False,
      failed=False,
      j=0,
      a_lo=a_lo,
      phi_lo=phi_lo,
      dphi_lo=dphi_lo,
      a_hi=a_hi,
      phi_hi=phi_hi,
      dphi_hi=dphi_hi,
      a_rec=(a_lo + a_hi) / 2.,
      phi_rec=(phi_lo + phi_hi) / 2.,
      a_star=1.0,
      phi_star=phi_lo,
      dphi_star=dphi_lo,
      g_star=g_0,
      nfev=0,
      ngev=0,
      # the auxiliary values are not used in the body of the loop
      # but are just set at the end, so we need them to have matching shapes
      # and dtypes
      aux_lo=aux,
      aux_hi=aux,
      aux_star=aux,
  )
  delta1 = 0.2
  delta2 = 0.1

  def body(state):
    # Body of zoom algorithm. We use boolean arithmetic to avoid using jax.cond
    # so that it works on GPU/TPU.
    dalpha = (state.a_hi - state.a_lo)
    a = jnp.minimum(state.a_hi, state.a_lo)
    b = jnp.maximum(state.a_hi, state.a_lo)
    cchk = delta1 * dalpha
    qchk = delta2 * dalpha

    # This will cause the line search to stop, and since the Wolfe conditions
    # are not satisfied the minimization should stop too.
    threshold = jnp.where((jnp.finfo(dalpha).bits < 64), 1e-5, 1e-10)
    state = state._replace(failed=state.failed | (dalpha <= threshold))

    # Cubmin is sometimes nan, though in this case the bounds check will fail.
    a_j_cubic = _cubicmin(state.a_lo, state.phi_lo, state.dphi_lo, state.a_hi,
                          state.phi_hi, state.a_rec, state.phi_rec)
    use_cubic = (state.j > 0) & (a_j_cubic > a + cchk) & (a_j_cubic < b - cchk)
    a_j_quad = _quadmin(state.a_lo, state.phi_lo, state.dphi_lo, state.a_hi, state.phi_hi)
    use_quad = (~use_cubic) & (a_j_quad > a + qchk) & (a_j_quad < b - qchk)
    a_j_bisection = (state.a_lo + state.a_hi) / 2.
    use_bisection = (~use_cubic) & (~use_quad)

    a_j = jnp.where(use_cubic, a_j_cubic, state.a_rec)
    a_j = jnp.where(use_quad, a_j_quad, a_j)
    a_j = jnp.where(use_bisection, a_j_bisection, a_j)

    # TODO(jakevdp): should we use some sort of fixed-point approach here instead?
    if has_aux:
      (phi_j, dphi_j, g_j), aux_j = restricted_func_and_grad(a_j)
    else:
      phi_j, dphi_j, g_j = restricted_func_and_grad(a_j)
      aux_j = jnp.nan
    phi_j = phi_j.astype(state.phi_lo.dtype)
    dphi_j = dphi_j.astype(state.dphi_lo.dtype)
    #g_j = g_j.astype(state.g_star.dtype)
    state = state._replace(nfev=state.nfev + 1,
                           ngev=state.ngev + 1)

    hi_to_j = wolfe_one(a_j, phi_j) | (phi_j >= state.phi_lo)
    star_to_j = wolfe_two(dphi_j) & (~hi_to_j)
    hi_to_lo = (dphi_j * (state.a_hi - state.a_lo) >= 0.) & (~hi_to_j) & (~star_to_j)
    lo_to_j = (~hi_to_j) & (~star_to_j)

    state = state._replace(
        **_binary_replace(
            hi_to_j,
            state._asdict(),
            dict(
                a_hi=a_j,
                phi_hi=phi_j,
                dphi_hi=dphi_j,
                aux_hi=aux_j,
                a_rec=state.a_hi,
                phi_rec=state.phi_hi,
            ),
        ),
    )

    # for termination
    state = state._replace(
        done=star_to_j | state.done,
        **_binary_replace(
            star_to_j,
            state._asdict(),
            dict(
                a_star=a_j,
                phi_star=phi_j,
                dphi_star=dphi_j,
                g_star=g_j,
                aux_star=aux_j,
            )
        ),
    )
    state = state._replace(
        **_binary_replace(
            hi_to_lo,
            state._asdict(),
            dict(
                a_hi=state.a_lo,
                phi_hi=state.phi_lo,
                dphi_hi=state.dphi_lo,
                aux_hi=state.aux_lo,
                a_rec=state.a_hi,
                phi_rec=state.phi_hi,
            ),
        ),
    )
    state = state._replace(
        **_binary_replace(
            lo_to_j,
            state._asdict(),
            dict(
                a_lo=a_j,
                phi_lo=phi_j,
                dphi_lo=dphi_j,
                aux_lo=aux_j,
                a_rec=state.a_lo,
                phi_rec=state.phi_lo,
            ),
        ),
    )
    state = state._replace(j=state.j + 1)
    # Choose higher cutoff for maxiter than Scipy as Jax takes longer to find
    # the same value - possibly floating point issues?
    state = state._replace(failed= state.failed | (state.j >= 30))

    # For dtype consistency
    state = state._replace(a_lo=state.a_lo.astype(init_state.a_lo.dtype),
                           a_hi=state.a_hi.astype(init_state.a_hi.dtype),
                           a_rec=state.a_rec.astype(init_state.a_rec.dtype))

    return state

  state = lax.while_loop(lambda state: (~state.done) & (~pass_through) & (~state.failed),
                         body,
                         init_state)

  return state


class _LineSearchState(NamedTuple):
  done: Union[bool, jnp.ndarray]
  failed: Union[bool, jnp.ndarray]
  i: Union[int, jnp.ndarray]
  a_i1: Union[float, jnp.ndarray]
  phi_i1: Union[float, jnp.ndarray]
  dphi_i1: Union[float, jnp.ndarray]
  nfev: Union[int, jnp.ndarray]
  ngev: Union[int, jnp.ndarray]
  a_star: Union[float, jnp.ndarray]
  phi_star: Union[float, jnp.ndarray]
  dphi_star: Union[float, jnp.ndarray]
  g_star: jnp.ndarray
  aux_star: Union[float, jnp.ndarray]


class _LineSearchResults(NamedTuple):
  """Results of line search.
  Parameters:
    failed: True if the strong Wolfe criteria were satisfied
    nit: integer number of iterations
    nfev: integer number of functions evaluations
    ngev: integer number of gradients evaluations
    k: integer number of iterations
    a_k: integer step size
    f_k: final function value
    g_k: final gradient value
    status: integer end status
  """
  failed: Union[bool, jnp.ndarray]
  nit: Union[int, jnp.ndarray]
  nfev: Union[int, jnp.ndarray]
  ngev: Union[int, jnp.ndarray]
  k: Union[int, jnp.ndarray]
  a_k: Union[int, jnp.ndarray]
  f_k: jnp.ndarray
  g_k: jnp.ndarray
  status: Union[bool, jnp.ndarray]
  aux: Union[float, jnp.ndarray]


def zoom_linesearch(f, xk, pk, old_fval=None, old_old_fval=None, gfk=None,
                    c1=1e-4, c2=0.9, maxiter=20, value_and_grad=False,
                    has_aux=False, aux=None, args=[], kwargs={}):
  """Inexact line search that satisfies strong Wolfe conditions.
  Algorithm 3.5 from Wright and Nocedal, 'Numerical Optimization', 1999,
  pages 59-61.

  Args:
    f: function of the form f(x) where x is a flat ndarray and returns a real
      scalar. The function should be composed of operations with vjp defined.
    x0: initial guess.
    pk: direction to search in. Assumes the direction is a descent direction.
    old_fval, gfk: initial value of value_and_gradient as position.
    old_old_fval: unused argument, only for scipy API compliance.
    maxiter: maximum number of iterations to search
    c1, c2: Wolfe criteria constant, see ref.
    value_and_grad: whether f returns just the value (False) or the value and
      grad (True).
    has_aux: if ``False``, ``f`` should return the function value only.
      If ``True``, ``f`` should return a pair ``(value, aux)`` where ``aux``
      is a pytree of auxiliary values.
    aux: auxiliary pytree data example for ``f``.
    args, kwargs: optional positional and keywords arguments to be passed to f.
  Returns: LineSearchResults
  """
  #xk, pk = _promote_dtypes_inexact(xk, pk)
  #xk = jnp.asarray(xk)
  #pk = jnp.asarray(pk)

  if value_and_grad:
    f_value_and_grad = f
  else:
    f_value_and_grad = jax.value_and_grad(f, has_aux=has_aux)

  def restricted_func_and_grad(t):
    dtype = tree_single_dtype(xk)
    if dtype is not None:
      t = jnp.asarray(t, dtype=dtype)
    xkp1 = tree_add_scalar_mul(xk, t, pk)
    if has_aux:
      (phi, aux), g = f_value_and_grad(xkp1, *args, **kwargs)
    else:
      phi, g = f_value_and_grad(xkp1, *args, **kwargs)
    dphi = jnp.real(tree_vdot(g, pk))
    if has_aux:
      return (phi, dphi, g), aux
    else:
      return phi, dphi, g

  if old_fval is None or gfk is None or (aux is None and has_aux):
    if has_aux:
      (phi_0, dphi_0, gfk), aux = restricted_func_and_grad(0)
    else:
      phi_0, dphi_0, gfk = restricted_func_and_grad(0)
  else:
    phi_0 = old_fval
    dphi_0 = jnp.real(tree_vdot(gfk, pk))
  if not has_aux:
    aux = jnp.nan
  if old_old_fval is not None:
    candidate_start_value = 1.01 * 2 * (phi_0 - old_old_fval) / dphi_0
    start_value = jnp.where(candidate_start_value > 1, 1.0, candidate_start_value)
  else:
    start_value = 1

  def wolfe_one(a_i, phi_i):
    # actually negation of W1
    return phi_i > phi_0 + c1 * a_i * dphi_0

  def wolfe_two(dphi_i):
    return jnp.abs(dphi_i) <= -c2 * dphi_0

  state = _LineSearchState(
      done=False,
      failed=False,
      # algorithm begins at 1 as per Wright and Nocedal, however Scipy has a
      # bug and starts at 0. See https://github.com/scipy/scipy/issues/12157
      i=1,
      a_i1=jnp.zeros([], dtype=phi_0.dtype),
      phi_i1=phi_0,
      dphi_i1=dphi_0,
      nfev=1 if (old_fval is None or gfk is None) else 0,
      ngev=1 if (old_fval is None or gfk is None) else 0,
      a_star=0.0,
      phi_star=phi_0,
      dphi_star=dphi_0,
      g_star=gfk,
      aux_star=aux,
  )

  def body(state):
    # no amax in this version, we just double as in scipy.
    # unlike original algorithm we do our next choice at the start of this loop
    a_i = jnp.where(state.i == 1, start_value, state.a_i1 * 2.)

    if has_aux:
      (phi_i, dphi_i, g_i), aux_i = restricted_func_and_grad(a_i)
    else:
      phi_i, dphi_i, g_i = restricted_func_and_grad(a_i)
      aux_i = jnp.nan
    state = state._replace(nfev=state.nfev + 1,
                           ngev=state.ngev + 1)

    star_to_zoom1 = wolfe_one(a_i, phi_i) | ((phi_i >= state.phi_i1) & (state.i > 1))
    star_to_i = wolfe_two(dphi_i) & (~star_to_zoom1)
    star_to_zoom2 = (dphi_i >= 0.) & (~star_to_zoom1) & (~star_to_i)

    zoom1 = _zoom(restricted_func_and_grad,
                  wolfe_one,
                  wolfe_two,
                  state.a_i1,
                  state.phi_i1,
                  state.dphi_i1,
                  a_i,
                  phi_i,
                  dphi_i,
                  gfk,
                  ~star_to_zoom1,
                  has_aux,
                  aux_i)

    state = state._replace(nfev=state.nfev + zoom1.nfev,
                           ngev=state.ngev + zoom1.ngev)

    zoom2 = _zoom(restricted_func_and_grad,
                  wolfe_one,
                  wolfe_two,
                  a_i,
                  phi_i,
                  dphi_i,
                  state.a_i1,
                  state.phi_i1,
                  state.dphi_i1,
                  gfk,
                  ~star_to_zoom2,
                  has_aux,
                  aux_i)

    state = state._replace(nfev=state.nfev + zoom2.nfev,
                           ngev=state.ngev + zoom2.ngev)

    state = state._replace(
        done=star_to_zoom1 | state.done,
        failed=(star_to_zoom1 & zoom1.failed) | state.failed,
        **_binary_replace(
            star_to_zoom1,
            state._asdict(),
            zoom1._asdict(),
            keys=['a_star', 'phi_star', 'dphi_star', 'g_star', 'aux_star'],
        ),
    )
    state = state._replace(
        done=star_to_i | state.done,
        **_binary_replace(
            star_to_i,
            state._asdict(),
            dict(
                a_star=a_i,
                phi_star=phi_i,
                dphi_star=dphi_i,
                g_star=g_i,
                aux_star=aux_i,
            ),
        ),
    )
    state = state._replace(
        done=star_to_zoom2 | state.done,
        failed=(star_to_zoom2 & zoom2.failed) | state.failed,
        **_binary_replace(
            star_to_zoom2,
            state._asdict(),
            zoom2._asdict(),
            keys=['a_star', 'phi_star', 'dphi_star', 'g_star', 'aux_star'],
        ),
    )
    state = state._replace(i=state.i + 1, a_i1=a_i, phi_i1=phi_i, dphi_i1=dphi_i)
    return state

  state = lax.while_loop(lambda state: (~state.done) & (state.i <= maxiter) & (~state.failed),
                         body,
                         state)

  status = jnp.where(
      state.failed,
      jnp.array(1),  # zoom failed
          jnp.where(
              state.i > maxiter,
              jnp.array(3),  # maxiter reached
              jnp.array(0),  # passed (should be)
          ),
  )
  # Step sizes which are too small causes the optimizer to get stuck with a
  # direction of zero in <64 bit mode - avoid with a floor on minimum step size.
  alpha_k = state.a_star
  alpha_k = jnp.where((jnp.finfo(alpha_k).bits != 64)
                    & (jnp.abs(alpha_k) < 1e-8),
                      jnp.sign(alpha_k) * 1e-8,
                      alpha_k)
  param_dtype = tree_single_dtype(xk)
  results = _LineSearchResults(
      failed=state.failed | (~state.done),
      nit=state.i - 1,  # because iterations started at 1
      nfev=state.nfev,
      ngev=state.ngev,
      k=state.i,
      a_k=alpha_k.astype(param_dtype),
      f_k=state.phi_star,
      aux=state.aux_star,
      g_k=state.g_star,
      status=status,
  )
  return results
