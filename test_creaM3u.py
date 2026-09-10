import ast
import re
import unittest
from pathlib import Path


def cargar_extraer_nombre_y_numero_disco():
    """Carga la función bajo prueba sin ejecutar el programa interactivo."""
    ruta_script = Path(__file__).with_name("creaM3u.py")
    arbol = ast.parse(ruta_script.read_text(encoding="utf-8"), filename=str(ruta_script))
    definicion = next(
        nodo
        for nodo in arbol.body
        if isinstance(nodo, ast.FunctionDef)
        and nodo.name == "extraer_nombre_y_numero_disco"
    )
    espacio_de_nombres = {"re": re}
    exec(compile(ast.Module(body=[definicion], type_ignores=[]), str(ruta_script), "exec"), espacio_de_nombres)
    return espacio_de_nombres["extraer_nombre_y_numero_disco"]


extraer_nombre_y_numero_disco = cargar_extraer_nombre_y_numero_disco()


class ExtraerNombreYNumeroDiscoTests(unittest.TestCase):
    def test_extrae_discos_entre_parentesis(self):
        casos = (
            ("Final Fantasy VII (disc 1).bin", ("Final Fantasy VII", 1)),
            ("Final Fantasy VII (DISC 2).bin", ("Final Fantasy VII", 2)),
        )

        for archivo, esperado in casos:
            with self.subTest(archivo=archivo):
                self.assertEqual(extraer_nombre_y_numero_disco(archivo), esperado)


    def test_extrae_discos_entre_parentesis_con_numero_discos(self):
        casos = (
            ("Aura Battler Dunbine (1991)(Family Soft)(jp)(Disk 1 of 6).zip", ("Aura Battler Dunbine (1991)(Family Soft)(jp)", 1)),
            ("Aura Battler Dunbine (1991)(Family Soft)(jp)(Disk 2 of 6).zip", ("Aura Battler Dunbine (1991)(Family Soft)(jp)", 2)),
            ("Aura Battler Dunbine (1991)(Family Soft)(jp)(Disk 3 of 6).zip", ("Aura Battler Dunbine (1991)(Family Soft)(jp)", 3)),
        )

        for archivo, esperado in casos:
            with self.subTest(archivo=archivo):
                self.assertEqual(extraer_nombre_y_numero_disco(archivo), esperado)


    def test_extrae_discos_entre_corchetes(self):
        self.assertEqual(
            extraer_nombre_y_numero_disco("Metal Gear Solid [disc 3].cue"),
            ("Metal Gear Solid", 3),
        )

    def test_extrae_discos_con_prefijo_cd(self):
        casos = (
            ("Chrono Cross CD 1.iso", ("Chrono Cross", 1)),
            ("Chrono Cross CD2.iso", ("Chrono Cross", 2)),
            ("chrono cross cd 10.iso", ("chrono cross", 10)),
        )

        for archivo, esperado in casos:
            with self.subTest(archivo=archivo):
                self.assertEqual(extraer_nombre_y_numero_disco(archivo), esperado)




    def test_ignora_espacios_extra_en_el_nombre_base(self):
        self.assertEqual(
            extraer_nombre_y_numero_disco("  Resident Evil   (disc 2).bin"),
            ("Resident Evil", 2),
        )

    def test_devuelve_none_para_archivos_sin_numero_de_disco(self):
        casos = (
            "Super Mario World.sfc",
            "Game (disc).bin",
            "Game CD.bin",
        )

        for archivo in casos:
            with self.subTest(archivo=archivo):
                self.assertEqual(extraer_nombre_y_numero_disco(archivo), (None, None))


if __name__ == "__main__":
    unittest.main()


