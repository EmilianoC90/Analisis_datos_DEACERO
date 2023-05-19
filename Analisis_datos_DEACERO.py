import requests
import pandas as pd
import matplotlib.pyplot as plt

data_response =  requests.get(f"https://analytics.deacero.com/api/teenus/get-data/c744a2a4-ab89-5432-b5e6-9f320162e160")
maintable = data_response.json()
df = pd.DataFrame(maintable)

# Obtener las columnas de la tabla
#columnas = df.columns
#print(columnas)

# Eliminar varias columnas por nombre
columnas_a_eliminar = ['lead_time', 'arrival_date_year', 'arrival_date_month', 'arrival_date_week_number', 
 'arrival_date_day_of_month', 'adults', 'children', 'babies', 'meal', 'distribution_channel', 'previous_cancellations', 
 'previous_bookings_not_canceled', 'reserved_room_type', 'assigned_room_type', 'booking_changes', 'deposit_type', 'agent',
 'company', 'days_in_waiting_list', 'customer_type', 'required_car_parking_spaces', 'total_of_special_requests']
for columna in columnas_a_eliminar:
    del df[columna]

# Valor a eliminar
valor_a_eliminar = "NULL"

# Obtener lista de columnas
columnas = df.columns

# Iterar sobre las columnas
for columna in columnas:
    # Generar condición booleana para la columna actual
    condicion = df[columna] == valor_a_eliminar

    # Eliminar filas que cumplan la condición
    df = df.drop(df[condicion].index)

df_correlation = df

hotel_urbano = 'City Hotel'
hotel_resort = 'Resort Hotel'

df_urbano = df.loc[df['hotel'] == hotel_urbano]
df_resort = df.loc[df['hotel'] == hotel_resort]


def plot_city_frequencies(df_urbano, df_resort, top_n=20):

    #Eliminar las filas canceladas
    df_urbano = df_urbano[df_urbano['is_canceled'] != '1']
    df_resort = df_resort[df_resort['is_canceled'] != '1']
    df_urbano = df_urbano[df_urbano['is_repeated_guest'] != '1']
    df_resort = df_resort[df_resort['is_repeated_guest'] != '1']

    # Calcular la frecuencia de cada ciudad
    frecuencia_ciudades_urbano = df_urbano['country'].value_counts().sort_values(ascending=False)
    frecuencia_ciudades_resort = df_resort['country'].value_counts().sort_values(ascending=False)


    # Obtener las primeras "top_n" ciudades y su frecuencia
    top_ciudades =frecuencia_ciudades_urbano.head(top_n)
    top_ciudades =frecuencia_ciudades_resort.head(top_n)

    # Sumar la frecuencia del resto de las ciudades
    frecuencia_otros_urbano = frecuencia_ciudades_urbano[20:].sum()
    frecuencia_otros_resort = frecuencia_ciudades_resort[20:].sum()


    # Crear una nueva serie con las primeras "top_n" ciudades y el resto agrupado como "Otros"
    frecuencia_final_urbano = top_ciudades._append(pd.Series({'Otros': frecuencia_otros_urbano}))
    frecuencia_final_resort = top_ciudades._append(pd.Series({'Otros': frecuencia_otros_resort}))

    # Crear la figura y las subtramas
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Graficar las barras en la primera subtrama
    ax1.bar(frecuencia_final_urbano.index, frecuencia_final_urbano, label='City Hotel', color= 'red')
    ax1.set_xlabel('Ciudad')
    ax1.set_ylabel('Frecuencia')
    ax1.set_title('Frecuencia de aparición de ciudades en City Hotel')
    ax1.legend()

    # Graficar las barras en la segunda subtrama
    ax2.bar(frecuencia_final_resort.index, frecuencia_final_resort, label='Resort Hotel')
    ax2.set_xlabel('Ciudad')
    ax2.set_ylabel('Frecuencia')
    ax2.set_title('Frecuencia de aparición de ciudades en Resort Hotel')
    ax2.legend()

    # Agregar los valores en las barras
    for i, v in enumerate(frecuencia_final_urbano):
        ax1.text(i, v, str(v), ha='center', va='bottom')

    for i, v in enumerate(frecuencia_final_resort):
        ax2.text(i, v, str(v), ha='center', va='bottom')
        
    # Ajustar los espacios entre las subtramas
    fig.tight_layout()

    # Mostrar la gráfica
    plt.show()

plot_city_frequencies(df_urbano,df_resort)

def plot_mensual_cost(df_urbano, df_resort):

    #Eliminar las filas canceladas
    df_urbano = df_urbano[df_urbano['is_canceled'] != '1']
    df_resort = df_resort[df_resort['is_canceled'] != '1']

    #Convertir la columna 'adr' a tipo float
    df_urbano.loc[ :, 'adr'] = df_urbano['adr'].astype(float)
    df_resort.loc[ :, 'adr'] = df_resort['adr'].astype(float)

    # Convertir la columna 'reservation_status_date' a tipo datetime
    df_urbano['reservation_status_date'] = pd.to_datetime(df_urbano['reservation_status_date'], format='%d/%m/%Y', errors='coerce')
    df_resort['reservation_status_date'] = pd.to_datetime(df_resort['reservation_status_date'], format='%d/%m/%Y', errors='coerce')
    
    # Calcular el precio promedio
    precio_prom_urbano = df_urbano['adr'].mean()
    print("Precio promedio por noche Hotel City: ", precio_prom_urbano)
    precio_prom_resort = df_resort['adr'].mean()
    print("Precio promedio por noche Hotel Resort: ",precio_prom_resort)

    # Verificar si hay registros con fecha nula
    if df_urbano['reservation_status_date'].isnull().any() or df_resort['reservation_status_date'].isnull().any():
        print("Se encontraron registros con formato de fecha inválido.")

    # Calcular el precio promedio por mes
    precio_promedio_urbano = df_urbano.groupby(df_urbano['reservation_status_date'].dt.to_period('M'))['adr'].mean()
    precio_promedio_resort = df_resort.groupby(df_resort['reservation_status_date'].dt.to_period('M'))['adr'].mean()

    # Crear la gráfica de barras
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    precio_promedio_urbano.plot(kind='line', ax=ax1)
    precio_promedio_resort.plot(kind='line', ax=ax2)

    # Configurar etiquetas y título
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Precio mensual por noche')
    ax1.set_title('Precio Promedio Mensual  - City Hotel')

    ax2.set_xlabel('Fecha')
    ax2.set_ylabel('Precio promedio mensual por noche')
    ax2.set_title('Precio Promedio Mensual - Resort Hotel')

    # Ajustar los espacios entre las subfiguras
    plt.tight_layout()

    # Mostrar la gráfica
    plt.show()

plot_mensual_cost(df_urbano, df_resort)

def plot_mensual_stay(df_urbano, df_resort, top_n=5):

    # Convertir las columnas 'stays_in_weekend_nights' y 'stays_in_week_nights' a tipo float
    df_urbano.loc[:, 'stays_in_weekend_nights'] = df_urbano['stays_in_weekend_nights'].astype(float)
    df_resort.loc[:, 'stays_in_weekend_nights'] = df_resort['stays_in_weekend_nights'].astype(float)
    df_urbano.loc[:, 'stays_in_week_nights'] = df_urbano['stays_in_week_nights'].astype(float)
    df_resort.loc[:, 'stays_in_week_nights'] = df_resort['stays_in_week_nights'].astype(float)
    
    # Calcular la cantidad total de noches de estadía
    df_noches_urbano = df_urbano['stays_in_weekend_nights'] + df_urbano['stays_in_week_nights']
    df_noches_resort = df_resort['stays_in_weekend_nights'] + df_resort['stays_in_week_nights']

    # Obtener la frecuencia de las noches de estadía
    frecuencia_urbano = df_noches_urbano.value_counts()
    frecuencia_resort =df_noches_resort.value_counts()

    # Obtener las primeras "top_n"
    top_noches_urbano =frecuencia_urbano.head(top_n)
    top_noches_resort =frecuencia_resort.head(top_n)

    # Sumar la frecuencia del resto 
    frecuencia_otros_urbano = frecuencia_urbano[20:].sum()
    frecuencia_otros_resort = frecuencia_resort[20:].sum()


    # Crear una nueva serie con las primeras "top_n" y el resto agrupado como "Otros"
    frecuencia_final_urbano = top_noches_urbano._append(pd.Series({'Otros': frecuencia_otros_urbano}))
    frecuencia_final_resort = top_noches_resort._append(pd.Series({'Otros': frecuencia_otros_resort}))




    # Eliminar las filas canceladas
    df_urbano = df_urbano[df_urbano['is_canceled'] != '1']
    df_resort = df_resort[df_resort['is_canceled'] != '1']

    # Convertir la columna 'reservation_status_date' a tipo datetime
    df_urbano['reservation_status_date'] = pd.to_datetime(df_urbano['reservation_status_date'], format='%d/%m/%Y', errors='coerce')
    df_resort['reservation_status_date'] = pd.to_datetime(df_resort['reservation_status_date'], format='%d/%m/%Y', errors='coerce')
    
    # Verificar si hay registros con fecha nula
    if df_urbano['reservation_status_date'].isnull().any() or df_resort['reservation_status_date'].isnull().any():
        print("Se encontraron registros con formato de fecha inválido.")

    # Obtener la frecuencia mensual de cancelaciones
    reservado_mensuales_urbano = df_urbano.groupby(df_urbano['reservation_status_date'].dt.to_period('M')).size()
    reservado_mensuales_resort = df_resort.groupby(df_resort['reservation_status_date'].dt.to_period('M')).size()

    # Crear la gráfica de barras
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    reservado_mensuales_urbano.plot(kind='line', ax=ax1)
    reservado_mensuales_resort.plot(kind='line', ax=ax2)

    # Configurar etiquetas y título
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Cantidad de reservas')
    ax1.set_title('Cantidad de reservas mensuales - City Hotel')

    ax2.set_xlabel('Fecha')
    ax2.set_ylabel('Cantidad de reservas')
    ax2.set_title('Cantidad de reservas mensuales - Resort Hotel')

    # Ajustar los espacios entre las subfiguras
    plt.tight_layout()

    # Crear la gráfica de pastel
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    frecuencia_final_urbano.plot(kind='pie', ax=ax1, autopct = '%.1f%%')
    frecuencia_final_resort.plot(kind='pie', ax=ax2, autopct = '%.1f%%')

    # Configurar etiquetas y título
    ax1.set_xlabel('Cantidad de noches')
    ax1.set_ylabel('Cantidad de reservas')
    ax1.set_title('Distribución de noches de estadía - City Hotel')

    ax2.set_xlabel('Cantidad de noches')
    ax2.set_ylabel('Cantidad de reservas')
    ax2.set_title('Distribución de noches de estadía - Resort Hotel')

    # Ajustar los espacios entre las subfiguras
    plt.tight_layout()

    # Mostrar la gráfica
    plt.show()

plot_mensual_stay(df_urbano, df_resort)

def plot_market_segment(df_urbano, df_resort):

    #Eliminar las filas canceladas
    df_urbano = df_urbano[df_urbano['is_canceled'] != '1']
    df_resort = df_resort[df_resort['is_canceled'] != '1']

    # Agrupar los datos por la columna 'market_segment' y contar el número de elementos en cada grupo
    segmentos_urbanos = df_urbano['market_segment'].value_counts()
    segmentos_resort = df_resort['market_segment'].value_counts()

    # Crear la gráfica de pastel para los segmentos urbanos
    plt.figure(figsize=(8, 6))
    segmentos_urbanos.plot(kind='pie', autopct='%1.1f%%')

    # Configurar etiquetas y título
    plt.title('Distribución de segmentos de mercado - City Hotel')

    # Mostrar la gráfica
    plt.show()

    # Crear la gráfica de pastel para los segmentos de resort
    plt.figure(figsize=(8, 6))
    segmentos_resort.plot(kind='pie', autopct='%1.1f%%')

    # Configurar etiquetas y título
    plt.title('Distribución de segmentos de mercado - Resort Hotel')

    # Mostrar la gráfica
    plt.show()

plot_market_segment(df_urbano, df_resort)

def plot_mensual_cancelation(df_urbano, df_resort):

    # Obtener la cantidad de cancelaciones por tipo de hotel
    cancelaciones_urbano = df_urbano['is_canceled'].value_counts()
    cancelaciones_resort = df_resort['is_canceled'].value_counts()

    print("Cancelaciones urbano: ", cancelaciones_urbano)
    print("Cancelaciones resort: ", cancelaciones_resort)
    
    canceled = '1'

    # Filtrar los registros de cancelaciones
    df_cancelaciones_urbano = df_urbano[df_urbano['is_canceled'] == canceled]
    df_cancelaciones_resort = df_resort[df_resort['is_canceled'] == canceled]

    # Convertir la columna 'reservation_status_date' a tipo datetime
    df_cancelaciones_urbano['reservation_status_date'] = pd.to_datetime(df_cancelaciones_urbano['reservation_status_date'], format='%d/%m/%Y', errors='coerce')
    df_cancelaciones_resort['reservation_status_date'] = pd.to_datetime(df_cancelaciones_resort['reservation_status_date'], format='%d/%m/%Y', errors='coerce')

    # Verificar si hay registros con fecha nula
    if df_cancelaciones_urbano['reservation_status_date'].isnull().any() or df_cancelaciones_resort['reservation_status_date'].isnull().any():
        print("Se encontraron registros con formato de fecha inválido.")

    # Obtener la frecuencia mensual de cancelaciones
    cancelaciones_mensuales_urbano = df_cancelaciones_urbano.groupby(df_cancelaciones_urbano['reservation_status_date'].dt.to_period('M')).size()
    cancelaciones_mensuales_resort = df_cancelaciones_resort.groupby(df_cancelaciones_resort['reservation_status_date'].dt.to_period('M')).size()

    # Crear la gráfica de barras
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    cancelaciones_mensuales_urbano.plot(kind='line', ax=ax1)
    cancelaciones_mensuales_resort.plot(kind='line', ax=ax2)

    # Configurar etiquetas y título
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Cantidad de cancelaciones')
    ax1.set_title('Cancelaciones Mensuales - City Hotel')

    ax2.set_xlabel('Fecha')
    ax2.set_ylabel('Cantidad de cancelaciones')
    ax2.set_title('Cancelaciones Mensuales - Resort Hotel')

    # Ajustar los espacios entre las subfiguras
    plt.tight_layout()

    # Mostrar la gráfica
    plt.show()

plot_mensual_cancelation(df_urbano, df_resort)

def correlation (df_correlation):

    

    # Convierte las columnas a tipo float
    df_correlation['is_canceled'] = df_correlation['is_canceled'].astype(float)
    df_correlation['stays_in_weekend_nights'] = df_correlation['stays_in_weekend_nights'].astype(float)
    df_correlation['stays_in_week_nights'] = df_correlation['stays_in_week_nights'].astype(float)
    df_correlation['adr'] = df_correlation['adr'].astype(float)

    # Calcula la tabla de correlación
    correlation_table = df_correlation[['is_canceled', 'stays_in_weekend_nights', 'stays_in_week_nights', 'adr']].corr()

    # Muestra la tabla de correlación
    print(correlation_table)

correlation(df_correlation)