#%% Bootstrap: carregue os magics do R (execute esta célula primeiro)
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"
os.environ["LC_ALL"] = "pt_BR.UTF-8"
# os.environ["R_HOME"] = r"C:\Program Files\R\R-4.4.1"
# os.environ["PATH"] = r"C:\Program Files\R\R-4.4.1\bin\x64;" + os.environ["PATH"]

# Carrega os magics do R
get_ipython().run_line_magic("load_ext", "rpy2.ipython")

#%% Python: crie seus dados normalmente
import pandas as pd
df_py = pd.DataFrame({"nome": ["Pedro","Ana","Lucas"], "idade": [18,25,21]})
df_py

#%% R: use o R dentro do .py (enviando df_py do Python para o R)
%%R -i df_py
print("No R, recebi df_py do Python:")
print(df_py)
summary(df_py)
# Exemplo: transformar no R
df_py$idade2 <- df_py$idade * 2

#%% Voltar do R para o Python (mesmo nome, sobrescrevendo)
%%R -o df_py
df_py  # agora com a coluna idade2 criada no R

#%% Python: continue o fluxo em Pandas
df_py.head()

#%% Rodar uma linha R “inline” sem abrir célula %%R
get_ipython().run_line_magic("R", 'cat("Media de idade no R:", mean(df_py$idade), "\\n")')
