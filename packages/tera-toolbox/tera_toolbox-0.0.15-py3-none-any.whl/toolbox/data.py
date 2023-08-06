# import requests
# from supabase import create_client


# url = "https://sygrjcqvvnsrvxczpnpx.supabase.co"
# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5Z3JqY3F2dm5zcnZ4Y3pwbnB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzU3MDgxMDUsImV4cCI6MTk5MTI4NDEwNX0.dK4303KKaNo4pE5ATtJdA0qukSVTsnMxAzWZjU30SW0"


# def holidays(calendar):
#     supabase = create_client(url, key)
#     response = supabase.table('feriados').select(
#         'data, descricao').eq('calendario', calendar).execute()
#     return response.data


def get_url(table, select=["*"], params={}):
    url = "https://sygrjcqvvnsrvxczpnpx.supabase.co/rest/v1/"
    url = url + table
    
    if select:
        select_string = ','.join(select)
        url = url +"?" +"select="+ select_string
        
    if params:
        key_value_pairs = [f'&{key}=eq.{value}' if not isinstance(value, list) else f'&{key}=in.({", ".join(map(str, value))})' for key, value in params.items()]
        params_string = ''.join(key_value_pairs)
        url = url + params_string

    return url

# def get_data_from_url(url=""):
#     headers = {
#         "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5Z3JqY3F2dm5zcnZ4Y3pwbnB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzU3MDgxMDUsImV4cCI6MTk5MTI4NDEwNX0.dK4303KKaNo4pE5ATtJdA0qukSVTsnMxAzWZjU30SW0",
#         "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN5Z3JqY3F2dm5zcnZ4Y3pwbnB4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzU3MDgxMDUsImV4cCI6MTk5MTI4NDEwNX0.dK4303KKaNo4pE5ATtJdA0qukSVTsnMxAzWZjU30SW0",
#     }   

#     response_register = requests.get(url, headers=headers)
#     returns = response_register.json()
#     return returns

def get_feriados(calendar="anbima"):
    url = get_url(table="feriados",select=['data','descricao'],params={'calendario':f'{calendar}'})
    return url

