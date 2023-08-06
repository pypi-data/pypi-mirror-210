use pyo3::prelude::*;
use ::pseudo_tilt::chern_character::{ChernChar, ChowGens, Δ};
use ::pseudo_tilt::tilt_stability::all_pseudo_semistabilizers;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn bogomolov_form(r: i32, c: i32, d: i32) -> PyResult<i32> {
    const P1: ChowGens = ChowGens{a: 1, b: 1, c: 1};
    let v = ChernChar::<P1>{r, c, d};
    Ok(Δ(&v))
}

#[pyfunction]
fn pseudo_semistabilizers(r: i32, c: i32, d: i32) -> PyResult<Vec<(i32, i32, i32)>> {
    const P1: ChowGens = ChowGens{a: 1, b: 1, c: 1};
    let v = ChernChar::<P1>{r, c, d};
    println!("Computing pseudo semistabilizers for {}", v);
    println!("");

    let output = all_pseudo_semistabilizers(&v)
        .ok_or_else(||
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>
            (format!("beta_min is irrational, hence infinite pseudo semistabilizers, quitting"))
        )?
        .map(|u| (u.r, u.c, u.d))
        .collect::<Vec<_>>();
    Ok(output)
}

/// A Python module implemented in Rust.
#[pymodule]
fn pseudo_tilt(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(bogomolov_form, m)?)?;
    m.add_function(wrap_pyfunction!(pseudo_semistabilizers, m)?)?;
    Ok(())
}
