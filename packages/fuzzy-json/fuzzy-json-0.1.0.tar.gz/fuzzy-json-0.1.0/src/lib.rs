extern crate pyo3;
use pyo3::exceptions;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

extern crate fuzzy_json;
use fuzzy_json::fson;

macro_rules! raise {
    ($( $params:expr ),*) => {
        Err(exceptions::PySystemError::new_err(format!( $( $params ),*)))
    };
}

#[pyfunction]
fn parse(source: &str) -> PyResult<String> {
    if let Some(data) = fson(source) {
        Ok(data)
    } else {
        raise!("cannot parse")
    }
}

#[pymodule]
fn fuzzy_json(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
