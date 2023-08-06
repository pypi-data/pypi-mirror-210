import matplotlib.pyplot as plt


def grafica_barras_paises_ricos():
    paises = ['Estados Unidos', 'China', 'Japón', 'Alemania', 'India', 'Reino Unido', 'Francia', 'Italia',
              'Canadá', 'Brasil']
    billions = [26.854, 19.373, 4.409, 4.308, 3.736, 3.158, 2.923, 2.169, 2.089, 2.081]

    plt.bar(paises, billions)
    plt.xlabel('Países')
    plt.ylabel('PIB per cápita (USD)')
    plt.title('Top 10 países más ricos del mundo')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def grafica_lineal_envejecimiento_mexico():
    anios = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025, 2030]
    porcentaje = [16.0, 18.5, 21.3, 26.4, 30.9, 38.0, 47.7, 55.0, 61.0]

    plt.plot(anios, porcentaje, marker='o')
    plt.xlabel('Años')
    plt.ylabel('Índice de envejecimiento')
    plt.title('Índice de envejecimiento en México')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def grafica_pastel_mortalidad_infantil_mexico_causas():
    causas = ['Enfermedades respiratorias', 'Prematuridad', 'Malformaciones congénitas', 'Infecciones neonatales']
    mortalidad = [36, 29, 21, 14]

    plt.pie(mortalidad, labels=causas, autopct='%1.1f%%')
    plt.title('Causas de Mortalidad en menores de un año en México')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

def grafica_pastel_mortalidad_infantil_mexico_sexo():
    sexo = ['Hombres', 'Mujeres']
    mortalidad = [10774, 8450]

    plt.pie(mortalidad, labels=sexo, autopct='%1.1f%%')
    plt.title('Mortalidad en menores de un año en México por sexo')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


# Ejecutar las funciones para mostrar las gráficas
grafica_barras_paises_ricos()
grafica_lineal_envejecimiento_mexico()
grafica_pastel_mortalidad_infantil_mexico_sexo()
grafica_pastel_mortalidad_infantil_mexico_causas()
