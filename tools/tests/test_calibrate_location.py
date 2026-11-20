"""仅使用合成数据验证数学与错误路径，不代表现场验收。"""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('calibration', Path(__file__).parents[1] / 'calibrate_location.py')
calibration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calibration)


def samples(mirror=False):
    result = []
    for i, (x, y) in enumerate([(0, 0), (4, 0), (0, 4), (1, 2), (3, 3)]):
        sy = -y if mirror else y
        result.append(dict(id=str(i), use='fit' if i < 3 else 'check',
                           source=[x, sy], plan=[10 - 2*y, 20 + 2*x]))
    return result


class CalibrationTests(unittest.TestCase):
    def test_rotation_translation_scale(self):
        report = calibration.calibrate(samples(), 0.01)
        self.assertEqual(report['status'], 'geometry_pass')
        self.assertAlmostEqual(report['scale'], 2)
        self.assertAlmostEqual(report['rotation_degrees'], 90)

    def test_explicit_mirror(self):
        self.assertEqual(calibration.calibrate(samples(True), 0.01, True)['status'], 'geometry_pass')

    def test_independent_error_fails(self):
        points = samples()
        points[-1]['plan'][0] += 2
        self.assertEqual(calibration.calibrate(points, 1)['status'], 'geometry_fail')

    def test_degenerate_fit_rejected(self):
        points = samples()
        for i in range(3):
            points[i]['source'] = [i, 0]
        with self.assertRaises(ValueError):
            calibration.calibrate(points, 1)

    def test_missing_check_rejected(self):
        with self.assertRaises(ValueError):
            calibration.calibrate(samples()[:3], 1)

    def test_reused_fit_point_rejected(self):
        points = samples()
        points[-1]['plan'] = points[0]['plan'][:]
        with self.assertRaises(ValueError):
            calibration.calibrate(points, 1)


if __name__ == '__main__':
    unittest.main()
