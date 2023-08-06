pub mod error;
pub mod extension;

use crate::error::SgxPckExtensionError;
use crate::extension::SgxPckExtension;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{IntoPyDict, PyBytes};

impl std::convert::From<SgxPckExtensionError> for PyErr {
    fn from(err: SgxPckExtensionError) -> PyErr {
        PyException::new_err(err.to_string())
    }
}

#[pyfunction]
fn sgx_pck_extension_from_pem(py: Python<'_>, pem: &[u8]) -> PyResult<PyObject> {
    let pck_extension = SgxPckExtension::from_pem_certificate(pem)?;

    let map: Vec<(&str, PyObject)> = vec![
        ("ppid", PyBytes::new(py, &pck_extension.ppid).to_object(py)),
        (
            "compsvn",
            PyBytes::new(py, &pck_extension.tcb.compsvn).to_object(py),
        ),
        ("pcesvn", pck_extension.tcb.pcesvn.to_object(py)),
        (
            "cpusvn",
            PyBytes::new(py, &pck_extension.tcb.cpusvn).to_object(py),
        ),
        (
            "pceid",
            PyBytes::new(py, &pck_extension.pceid).to_object(py),
        ),
        (
            "fmspc",
            PyBytes::new(py, &pck_extension.fmspc).to_object(py),
        ),
        (
            "platform_instance_id",
            PyBytes::new(py, &pck_extension.platform_instance_id).to_object(py),
        ),
        (
            "dynamic_platform",
            pck_extension.configuration.dynamic_platform.to_object(py),
        ),
        (
            "cached_keys",
            pck_extension.configuration.cached_keys.to_object(py),
        ),
        (
            "smt_enabled",
            pck_extension.configuration.smt_enabled.to_object(py),
        ),
    ];

    Ok(map.into_py_dict(py).to_object(py))
}

#[pymodule]
#[pyo3(name = "_lib_sgx_pck_extension")]
fn sgx_pck_extension(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sgx_pck_extension_from_pem, m)?)?;
    Ok(())
}
