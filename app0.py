import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

@st.cache_resource
def load_data(file_data):
    try:
        return pd.read_csv(file_data, sep=';')
    except:
        return pd.read_excel(file_data)

@st.cache_resource
def multiselected_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)
    
@st.cache_resource
def df_to_string(df):
    return df.to_csv(index=False)

@st.cache_resource
def df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.close()
    processed_data = output.getvalue()
    return processed_data

def main():
    st.set_page_config(
        page_title = 'Telemarketing analisys',
        layout = 'wide',
        initial_sidebar_state = 'expanded'
    )

    st.write('# Telemarketing analisys')
    st.markdown('---')

    st.sidebar.write('## Suba o arquivo')
    data_file_1 = st.sidebar.file_uploader('Bank marketing data', type=['csv', 'xlsx'])

    if data_file_1 is not None:
        bank_raw = load_data(data_file_1)
        bank = bank_raw.copy()

        st.write('## Antes dos filtros')
        st.write(bank_raw.head())

        with st.sidebar.form(key='my_form'):

            graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))

            # IDADE
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.sidebar.slider(
                label = 'Idade',
                min_value = min_age,
                max_value = max_age,
                value = (min_age, max_age),
                step=1
            )

            st.sidebar.write('IDADES:', idades)
            st.sidebar.write('IDADE MIN:', idades[0])
            st.sidebar.write('IDADE MAX:', idades[1])

            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected = st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected = st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected = st.multiselect("Default", default_list, ['all'])

            # TEM FINANCIAMENTO IMOBILIARIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected = st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            # TEM EMPRESTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected = st.multiselect("Tem emprestimo?", loan_list, ['all'])

            # MEIO DE CONTATO
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected = st.multiselect("Meio de contato", contact_list, ['all'])

            # MES DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected = st.multiselect("Mes do contato", month_list, ['all'])

            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected = st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # Aplicar filtros
            bank = (bank.query('age >= @idades[0] and age <= @idades[1]')
                    .pipe(multiselected_filter, 'job', jobs_selected)
                    .pipe(multiselected_filter, 'marital', marital_selected)
                    .pipe(multiselected_filter, 'default', default_selected)
                    .pipe(multiselected_filter, 'housing', housing_selected)
                    .pipe(multiselected_filter, 'loan', loan_selected)
                    .pipe(multiselected_filter, 'contact', contact_selected)
                    .pipe(multiselected_filter, 'month', month_selected)
                    .pipe(multiselected_filter, 'day_of_week', day_of_week_selected)
            )

            submit_button = st.form_submit_button(label='Aplicar')

        st.write('## Após os filtros')
        st.write(bank.head())
        st.markdown('---')

        csv = df_to_string(bank)
        st.write(type(csv))
        st.write(csv[:100])

        st.write('### Download CSV')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv',
        )

        df_xlsx = df_to_excel(bank)
        st.write(type(df_xlsx))
        st.write(df_xlsx[:100])

        st.write('### Download Excel')
        st.download_button(
            label='📥 Download data as EXCEL',
            data=df_xlsx,
            file_name='filtered_data.xlsx',
        )

       # PLOTS    
        fig, ax = plt.subplots(1, 2, figsize = (5,3))

        bank_raw_target_perc = bank_raw.y.value_counts(normalize = True).to_frame()*100
        bank_raw_target_perc = bank_raw_target_perc.sort_index()
        
        try:
            bank_target_perc = bank.y.value_counts(normalize = True).to_frame()*100
            bank_target_perc = bank_target_perc.sort_index()
        except:
            st.error('Erro no filtro')

        col1, col2 = st.columns(2)

        df_xlsx = df_to_excel(bank_raw_target_perc)
        col1.write('### Proporção original')
        col1.write(bank_raw_target_perc)
        col1.download_button(label='📥 Download',
                            data=df_xlsx ,
                            file_name= 'bank_raw_y.xlsx')
        
        df_xlsx = df_to_excel(bank_target_perc)
        col2.write('### Proporção da tabela com filtros')
        col2.write(bank_target_perc)
        col2.download_button(label='📥 Download',
                            data=df_xlsx ,
                            file_name= 'bank_y.xlsx')
        st.markdown("---")
    

        st.write('## Proporção de aceite')

        # PLOTS    
        if graph_type == 'Barras':
            sns.barplot(x = bank_raw_target_perc.index, 
                        y = 'y',
                        data = bank_raw_target_perc, 
                        ax = ax[0])
            ax[0].bar_label(ax[0].containers[0])
            ax[0].set_title('Dados brutos',
                            fontweight ="bold")
            
            sns.barplot(x = bank_target_perc.index, 
                        y = 'y', 
                        data = bank_target_perc, 
                        ax = ax[1])
            ax[1].bar_label(ax[1].containers[0])
            ax[1].set_title('Dados filtrados',
                            fontweight ="bold")
        else:
            bank_raw_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax = ax[0])
            ax[0].set_title('Dados brutos',
                            fontweight ="bold")
            
            bank_target_perc.plot(kind='pie', autopct='%.2f', y='y', ax = ax[1])
            ax[1].set_title('Dados filtrados',
                            fontweight ="bold")

        st.pyplot(plt)

if __name__ == '__main__':
    main()
