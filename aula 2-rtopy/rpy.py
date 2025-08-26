#%% [BOOTSTRAP] Integração Python+R (execute esta célula primeiro)
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"
os.environ["LC_ALL"] = "pt_BR.UTF-8"
# Se o R não for detectado automaticamente, descomente e ajuste as linhas abaixo:
# os.environ["R_HOME"] = r"C:\Program Files\R\R-4.4.1"
# os.environ["PATH"] = r"C:\Program Files\R\R-4.4.1\bin\x64;" + os.environ["PATH"]

# Carrega os magics do R (rpy2)
get_ipython().run_line_magic("load_ext", "rpy2.ipython")

#%% [PYTHON] Carregamento do CSV e ajustes no pandas
import pandas as pd

# Exibir floats com 2 casas decimais
pd.options.display.float_format = "{:.2f}".format

# Ajuste o caminho conforme sua máquina
csv_path = r"C:\Lucas\IBMEC\4 Semestre\Inferencia estatística\Aula 2\Data\normtemp.csv"

# O arquivo usa ';' como separador
df_py = pd.read_csv(csv_path, sep=';')

# Arredonda a coluna de interesse (se o nome da coluna for "Temperatura")
if 'Temperatura' in df_py.columns:
    df_py['Temperatura'] = df_py['Temperatura'].round(2)

df_py.head()
%reload_ext rpy2.ipython
#%% [R] Análises no R usando o df do Python
%%R -i df_py

print("No R, recebi df_py do Python\n")
print(df_py)

# Pacotes (car inclui qqPlot)
if (!require("pacman")) install.packages("pacman", quiet=TRUE)
pacman::p_load(dplyr, rstatix, ggplot2, ggpubr, ggsignif,
               effectsize, ggbeeswarm, report, car, scales)

# Se "Genero" ainda estiver como texto, conferir níveis (pode retornar NULL se for character)
levels_try <- try(levels(df_py$Genero), silent = TRUE)
print(levels_try)

# Estrutura
glimpse(df_py)

# Ajuste de tipos
df_py$Genero <- factor(df_py$Genero)
glimpse(df_py)

# ------------ Análise descritiva por gênero -------------
desc <- df_py |>
  group_by(Genero) |>
  rstatix::get_summary_stats(Temperatura)
print(desc)

# Boxplot simples
boxplot(df_py$Temperatura ~ df_py$Genero, main="Boxplot por Gênero",
        ylab="Temperatura (ºC)", xlab="Gênero")

# ------------ Pressupostos do t-teste -------------
# Shapiro por grupo
print(df_py |>
  group_by(Genero) |>
  shapiro_test(Temperatura))

# QQPlot por grupo (usa pacote car)
car::qqPlot(x = df_py$Temperatura, groups = df_py$Genero, main="QQPlot por Gênero")

# Homogeneidade de variâncias (Levene)
print(rstatix::levene_test(data = df_py, Temperatura ~ Genero, center = "mean"))

# ------------ t-teste independente (variâncias iguais) -------------
tt <- t.test(Temperatura ~ Genero, data = df_py,
             alternative = "two.sided", var.equal = TRUE, paired = FALSE)
print(tt)

# Tamanho de efeito (d de Cohen) e interpretação
d <- effectsize::cohens_d(Temperatura ~ Genero, data = df_py, paired = FALSE)
print(d)
print(effectsize::interpret_cohens_d(d$Cohens_d, rules = "cohen1988"))
print(effectsize::interpret_cohens_d(d$Cohens_d, rules = "sawilowsky2009"))

# Média e desvio-padrão por grupo
md <- df_py |>
  group_by(Genero) |>
  get_summary_stats(Temperatura, type = "mean_sd") |>
  as.data.frame()
print(md)

# Diferença de médias (só exemplo – ajuste os valores se quiser calcular manualmente)
# dif <- 36.885 - 36.725
# print(dif)

# ------------ Gráfico (dotplot com média e IC 95%) -------------
g <- ggplot(data = df_py, aes(x = Genero, y = Temperatura)) +
  ggbeeswarm::geom_beeswarm(method = "center",
                            color = "cadetblue",
                            alpha = 0.7, cex = 4) +
  geom_crossbar(stat = "summary", fun = "mean", fatten = 1, width = 0.5) +
  geom_errorbar(stat = "summary", fun.data = "mean_sd", width = 0.15) +
  ggsignif::geom_signif(comparisons = list(c("Feminino", "Masculino")),
                        annotations = "*", vjust = 0.5,
                        textsize = 5, tip_length = 0.01) +
  scale_y_continuous(labels = scales::number_format(big.mark=".", decimal.mark=",")) +
  labs(y = "Temperatura (ºC)", x = "Gênero") +
  theme_classic()

print(g)

# Salvar em alta
ggsave("dotplot.png", plot = g, dpi = 600, width = 3.5, height = 3.5, units = "in")

# ------------ Report do teste -------------
resultado <- t.test(Temperatura ~ Genero, data = df_py,
                    alternative = "two.sided", paired = FALSE, var.equal = TRUE)
print(report::report(resultado))
#%% [R->PYTHON] Trazer df de volta ao Python (se tiver modificado algo no R)
%%R -o df_py
df_py
#%% [PYTHON] Conferir no pandas novamente
df_py.head()
