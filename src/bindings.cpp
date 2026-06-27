#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cstdint>
#include <stdexcept>
#include <string>

#include "validation.h"
#include "wire/byte_view.h"

namespace py = pybind11;

namespace {

fwfc::wire::ByteView as_view(py::buffer buffer) {
    py::buffer_info info = buffer.request();
    if (info.ndim != 1) {
        throw std::invalid_argument("expected 1-D buffer");
    }
    return {static_cast<const std::uint8_t*>(info.ptr), static_cast<std::size_t>(info.size)};
}

}  // namespace

PYBIND11_MODULE(_factorio_wfc, m) {
    m.doc() = "Factorio WFC grid engine";

    py::class_<fwfc::ValidationResult>(m, "ValidationResult")
        .def_readonly("is_valid", &fwfc::ValidationResult::is_valid)
        .def_readonly("message", &fwfc::ValidationResult::message);

    m.def("wire_format_version", &fwfc::wire_format_version);

    m.def(
        "load_catalog",
        [](py::buffer catalog_bytes) {
            std::string error;
            if (!fwfc::load_catalog_bytes(as_view(catalog_bytes), error)) {
                throw std::runtime_error(error);
            }
        },
        py::arg("catalog_bytes"));

    m.def(
        "validate_snapshot",
        [](std::uint32_t width, std::uint32_t height, py::buffer cells_bytes) {
            return fwfc::validate_snapshot(width, height, as_view(cells_bytes));
        },
        py::arg("width"),
        py::arg("height"),
        py::arg("cells_bytes"));
}
