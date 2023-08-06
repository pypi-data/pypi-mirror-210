use pyo3::prelude::*;

pub fn greet() {
    println!("Hello nix from rust!");
}

#[pyfunction]
pub fn rgreet() {
    greet();
}

#[pymodule]
fn rhello(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rgreet, m)?)?;
    Ok(())
}
