import streamlit as st
import py3Dmol
import subprocess
import zipfile
import os
from rdkit import Chem
from rdkit.Chem import AllChem

st.set_page_config(page_title="XTB Web Interface",
                   page_icon="⚛️")
st.sidebar.image("img/inXTB_logo.png", caption="Dr. Jesus Alvarado-Huayhuaz")

st.title("Cálculo con XTB")

# ==============================
# FUNCIONES
# ==============================

def visualize_xyz(xyz):

    view = py3Dmol.view(width=500, height=400)
    view.addModel(xyz, "xyz")
    view.setStyle({"stick":{}})
    view.zoomTo()

    return view._make_html()


def smiles_to_xyz(smiles):

    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)

    AllChem.EmbedMolecule(mol)
    AllChem.MMFFOptimizeMolecule(mol)

    conf = mol.GetConformer()

    xyz = f"{mol.GetNumAtoms()}\nSMILES molecule\n"

    for atom in mol.GetAtoms():
        pos = conf.GetAtomPosition(atom.GetIdx())
        xyz += f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n"

    return xyz


def run_xtb(command):

    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    return process.stdout, process.stderr


def zip_results():

    with zipfile.ZipFile("resultados.zip", "w") as zipf:

        for file in os.listdir():

            if file.endswith(".xyz") or file.endswith(".out"):
                zipf.write(file)

    return "resultados.zip"


# ==============================
# INPUT MOLECULAR
# ==============================

st.sidebar.header("Input molecular")

option = st.sidebar.radio(
    "Tipo de input",
    ["XYZ", "SMILES"]
)

# -----------------------------

if option == "XYZ":

    xyz_default = """3
molecula de agua
O     0.0000000    0.0000000   -0.3893611
H     0.7629844    0.0000000    0.1946806
H    -0.7629844    0.0000000    0.1946806
"""

    xyz_input = st.text_area(
        "Coordenadas XYZ",
        xyz_default,
        height=200
    )

    xyz = xyz_input

# -----------------------------

if option == "SMILES":

    smiles = st.text_input(
        "Código SMILES",
        "CCO"
    )

    xyz = smiles_to_xyz(smiles)

    st.subheader("XYZ generado")

    st.code(xyz)

# ==============================
# VISUALIZACIÓN INICIAL
# ==============================

st.subheader("Estructura inicial")

st.components.v1.html(
    visualize_xyz(xyz),
    height=450
)

# ==============================
# OPCIONES XTB
# ==============================

st.sidebar.header("Opciones XTB")

calc = st.sidebar.selectbox(
    "Tipo de cálculo",
    ["single point", "optimización", "frecuencias", "opt + frecuencias"]
)

charge = st.sidebar.number_input("Carga (--chrg)", value=0)

uhf = st.sidebar.number_input("Electrones desapareados (--uhf)", value=0)

solvent = st.sidebar.text_input(
    "Solvente (--gbsa)",
    ""
)

outfile = st.sidebar.text_input(
    "Archivo de salida",
    "resultado.out"
)

# ==============================
# CONSTRUIR COMANDO
# ==============================

flags = ""

if calc == "optimización":
    flags += " --opt"

if calc == "frecuencias":
    flags += " --hess"

if calc == "opt + frecuencias":
    flags += " --ohess"

flags += f" --chrg {charge}"
flags += f" --uhf {uhf}"

if solvent != "":
    flags += f" --gbsa {solvent}"

# ==============================
# EJECUTAR XTB
# ==============================

if st.button("Ejecutar cálculo XTB"):

    with open("input.xyz", "w") as f:
        f.write(xyz)

    command = f"xtb input.xyz {flags} > {outfile}"

    st.code(command)

    with st.spinner("Ejecutando XTB..."):

        stdout, stderr = run_xtb(command)

    st.success("Cálculo finalizado")

    # ==========================
    # MOSTRAR RESULTADO
    # ==========================

    if os.path.exists("xtbopt.xyz"):

        with open("xtbopt.xyz") as f:
            opt_xyz = f.read()

        st.subheader("Estructura optimizada")

        st.components.v1.html(
            visualize_xyz(opt_xyz),
            height=450
        )

    # ==========================
    # ZIP
    # ==========================

    zip_file = zip_results()

    with open(zip_file, "rb") as f:

        st.download_button(
            "Descargar resultados",
            f,
            file_name="resultados_xtb.zip"
        )
