from pathlib import Path
import importlib.util

MODULE_PATH = Path("student_solution.py")


def load_student_module():
    if not MODULE_PATH.exists():
        raise FileNotFoundError(
            "student_solution.py was not created. Run scripts/extract_notebook.py first."
        )
    spec = importlib.util.spec_from_file_location("student_solution", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_module_loads():
    mod = load_student_module()
    assert hasattr(mod, "Matrix")


def test_full_creates_matrix_with_requested_shape_and_value():
    mod = load_student_module()
    mat = mod.full(99, (2, 3))
    assert mat.shape == (2, 3)
    assert mat.array == [[99, 99, 99], [99, 99, 99]]


def test_get_scalar_row_and_column():
    mod = load_student_module()
    m = mod.Matrix([1, 2, 3], [4, 5, 6])
    assert mod.get(m, 1, 2) == 6
    row = mod.get(m, 0, None)
    assert row.shape == (1, 3)
    assert row.array == [[1, 2, 3]]
    col = mod.get(m, None, 1)
    assert col.shape == (2, 1)
    assert col.array == [[2], [5]]


def test_set_scalar_row_and_column():
    mod = load_student_module()
    m = mod.Matrix([1, 2], [3, 4])
    mod.set(m, 1, 0, 99)
    assert m.array == [[1, 2], [99, 4]]
    mod.set(m, 0, None, [7, 8])
    assert m.array[0] == [7, 8]
    mod.set(m, None, 1, [11, 12])
    assert m.array == [[7, 11], [99, 12]]


def test_equal_with_isclose_tolerance():
    mod = load_student_module()
    m1 = mod.Matrix([10.0, 20.0])
    m2 = mod.Matrix([10.4, 20.0])
    eq = mod.equal(m1, m2)
    assert eq.array == [[1, 1]]


def test_copy_returns_distinct_matrix():
    mod = load_student_module()
    m1 = mod.Matrix([1, 2], [3, 4])
    m2 = mod.copy(m1)
    assert m2.array == [[1, 2], [3, 4]]
    m1.array[0][0] = 999
    assert m2.array[0][0] == 1


def test_transpose():
    mod = load_student_module()
    m = mod.Matrix([1, 9], [2, 99], [3, 999])
    tm = mod.transpose(m)
    assert tm.shape == (2, 3)
    assert tm.array == [[1, 2, 3], [9, 99, 999]]


def test_flatten():
    mod = load_student_module()
    m = mod.Matrix([1, 9], [2, 99], [3, 999])
    fm = mod.flatten(m)
    assert fm.shape == (1, 6)
    assert fm.array == [[1, 9, 2, 99, 3, 999]]


def test_reshape():
    mod = load_student_module()
    m = mod.Matrix([1, 2, 3], [4, 5, 6])
    rm = mod.reshape(m, (3, 2))
    assert rm.shape == (3, 2)
    assert rm.array == [[1, 2], [3, 4], [5, 6]]


def test_compute():
    mod = load_student_module()
    m1 = mod.Matrix([1, 2], [3, 4])
    m2 = mod.Matrix([10, 20], [30, 40])
    cm = mod.compute(m1, m2, lambda a, b: a + b)
    assert cm.array == [[11, 22], [33, 44]]


def test_mean_row_wise_and_column_wise():
    mod = load_student_module()
    m = mod.Matrix([1, 2, 3], [4, 5, 6])
    row_means = mod.mean(m, True)
    assert row_means.array == [[2.0, 5.0]]
    col_means = mod.mean(m, False)
    assert col_means.array == [[2.5, 3.5, 4.5]]
