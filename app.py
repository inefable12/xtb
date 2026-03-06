import streamlit as st
import subprocess
import zipfile
import os

st.set_page_config(
    page_title="XTB Web Interface",
    page_icon="⚛️"
)

st.sidebar.image("img/inXTB_logo.png", caption="Dr. Jesus Alvarado-Huayhuaz")

st.title("Cálculo con XTB")

# ==============================
# INPUT MOLECULAR (solo XYZ)
# ==============================

st.sidebar.header("Input molecular")

xyz_default = """3
molecula de agua
O     0.0000000    0.0000000   -0.3893611
H     0.7629844    0.0000000    0.1946806
H    -0.7629844    0.0000000    0.1946806
"""

xyz = st.text_area(
    "Coordenadas XYZ",
    xyz_default,
    height=200
)

# ==============================
# OPCIONES XTB
# ==============================

st.sidebar.header("Opciones XTB")

calc = st.sidebar.selectbox(
    "Tipo de cálculo",
    ["single point", "optimización", "frecuencias", "opt + frecuencias"]
)

charge = st.sidebar.number_input(
    "Carga (--chrg)",
    value=0
)

uhf = st.sidebar.number_input(
    "Electrones desapareados (--uhf)",
    value=0
)

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

command = f"xtb input.xyz {flags} > {outfile}"

st.subheader("Comando generado")

st.code(command)

# ==============================
# FUNCIÓN PARA EJECUTAR XTB
# ==============================

def run_xtb(command):

    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )

    return process.stdout, process.stderr


# ==============================
# FUNCIÓN ZIP
# ==============================

def zip_results():

    with zipfile.ZipFile("resultados.zip", "w") as zipf:

        for file in os.listdir():

            if file.endswith(".xyz") or file.endswith(".out"):
                zipf.write(file)

    return "resultados.zip"


# ==============================
# EJECUTAR CÁLCULO
# ==============================

###################################################################
st.sidebar.header("Diagnóstico del sistema")

if st.sidebar.button("Verificar instalación de XTB"):

    st.subheader("Diagnóstico del entorno")

    # Mostrar PATH
    st.write("PATH del sistema:")
    st.code(os.environ.get("PATH"))

    # Verificar si xtb existe
    st.write("Ubicación de xtb:")

    result = subprocess.run(
        "which xtb",
        shell=True,
        capture_output=True,
        text=True
    )

    st.code(result.stdout if result.stdout else "xtb no encontrado")

    # Versión de xtb
    st.write("Versión de xtb:")

    version = subprocess.run(
        "xtb --version",
        shell=True,
        capture_output=True,
        text=True
    )

    st.code(version.stdout if version.stdout else version.stderr)
###################################################################

if st.button("Ejecutar cálculo XTB"):

    with open("input.xyz", "w") as f:
        f.write(xyz)

    with st.spinner("Ejecutando XTB..."):

        stdout, stderr = run_xtb(command)

        st.subheader("STDOUT")
        st.code(stdout)
        
        st.subheader("STDERR")
        st.code(stderr)

    st.success("Cálculo finalizado")

    # Mostrar salida si existe
    if os.path.exists(outfile):

        st.subheader("Salida del cálculo")

        with open(outfile) as f:
            st.text(f.read())

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
