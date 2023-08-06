from unittest import TestCase
import pytest


class General(TestCase):
    def test_import(self):
        import BNumMet

        assert BNumMet

    def test_import_visualizers(self):
        import BNumMet.Visualizers

        assert BNumMet.Visualizers

    def test_import_linearsystems_all(self):
        from BNumMet import LinearSystems

        assert LinearSystems.lu
        assert LinearSystems.interactive_lu
        assert LinearSystems.permute

    def test_import_interpolation_all(self):
        from BNumMet import Interpolation

        assert Interpolation.polinomial
        assert Interpolation.piecewise_linear
        assert Interpolation.pchip
        assert Interpolation.splines

    def test_import_nonlinear_all(self):
        from BNumMet import NonLinear

        assert NonLinear.bisect
        assert NonLinear.secant
        assert NonLinear.newton
        assert NonLinear.IQI
        assert NonLinear.zBrentDekker
