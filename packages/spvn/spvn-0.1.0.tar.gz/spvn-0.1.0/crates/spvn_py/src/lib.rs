use pyo3::prelude::*;
use simple_logger::SimpleLogger;

#[pyfunction]
fn bind() {}

#[pyclass]
struct PyConfig {

}

#[pymodule]
fn spvn(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    SimpleLogger::new().env().init().unwrap();

    Python::with_gil(|py| {
        assert!(py.version_info() >= (3, 10));
    });

    m.add_function(wrap_pyfunction!(bind, m)?)?;
    Ok(())
}
