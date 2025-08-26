#%% 🔧 Bootstrap (rode esta célula primeiro)
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"
os.environ["LC_ALL"] = "pt_BR.UTF-8"
# Se precisar apontar o R manualmente no Windows, descomente e ajuste:
# os.environ["R_HOME"] = r"C:\Program Files\R\R-4.4.1"
# os.environ["PATH"]  = r"C:\Program Files\R\R-4.4.1\bin\x64;" + os.environ["PATH"]

# Carrega os magics do R (ipykernel)
get_ipython().run_line_magic("load_ext", "rpy2.ipython")
print("Extensão %R carregada.")

#%% 🐍 [PYTHON] Carregamento do CSV e preparação do DataFrame
import pandas as pd

pd.options.display.float_format = "{:.2f}".format

# Ajuste o caminho do seu arquivo:
csv_path = r"C:\Users\lucas\IBMEC\programacao_para_analise_de_dados_2025.2\aula 2-rtopy\normtemp.csv"

# Separa por ';'
df_py = pd.read_csv(csv_path, sep=';')

# --- Normaliza nomes de colunas para evitar acentos/variações ---
orig_cols = df_py.columns.tolist()
norm = (df_py.columns
          .str.normalize('NFKD').str.encode('ascii','ignore').str.decode('ascii')
          .str.strip().str.lower())

df_py.columns = norm

# Mapeia nomes esperados para os do seu R: Genero / Temperatura
alvo_genero_alias   = {"genero","genero.","sexo","sex","gender"}
alvo_temp_alias     = {"temperatura","temp","temperature","bodytemp","body_temp","body.temperature"}

col_genero = next((c for c in df_py.columns if c in alvo_genero_alias), None)
col_temp   = next((c for c in df_py.columns if c in alvo_temp_alias), None)

if col_genero is None or col_temp is None:
    raise ValueError(
        f"Não achei as colunas de Gênero/Temperatura. Colunas atuais: {orig_cols}\n"
        f"Detectado genero={col_genero}, temperatura={col_temp}"
    )

# Renomeia para os nomes usados no R
df_py = df_py.rename(columns={col_genero: "Genero", col_temp: "Temperatura"})

# Converte Temperatura para float (funciona com vírgula decimal também)
df_py["Temperatura"] = (
    df_py["Temperatura"]
    .astype(str).str.replace(",", ".", regex=False)
    .astype(float).round(2)
)

# Garante 'Genero' como string (R fará factor)
df_py["Genero"] = df_py["Genero"].astype(str).str.strip()

# Remove linhas com NA em colunas críticas
df_py = df_py.dropna(subset=["Genero","Temperatura"]).reset_index(drop=True)

print(df_py.head())
print("Shape:", df_py.shape)

#%% 📦 [R] Pacotes + espelho CRAN (executa 1x por ambiente)
%%R
options(repos = c(CRAN = "https://cloud.r-project.org"))
if (!require("pacman")) install.packages("pacman", quiet=TRUE)
pacman::p_load(dplyr, rstatix, ggplot2, ggpubr, ggsignif,
               effectsize, ggbeeswarm, report, car, scales)

#%% 🇷 Envia df_py (Python) → R e ajusta objeto ex1_aula2
%%R -i df_py
# Usa o mesmo nome do seu script R
ex1_aula2 <- df_py

# Visão geral
print("Níveis de Genero (antes do factor):")
print(unique(ex1_aula2$Genero))

# Ajuste das variáveis
ex1_aula2$Genero <- factor(ex1_aula2$Genero)

# Conferência
print("Níveis de Genero (após factor):")
print(levels(ex1_aula2$Genero))

#%% 🇷 Análises descritivas (equivalente ao seu R)
%%R
# glimpse e "View" (View não abre via rpy2; usamos head)
dplyr::glimpse(ex1_aula2)
print(head(ex1_aula2, 10))

# Descritiva por gênero
desc_tbl <- ex1_aula2 |>
  dplyr::group_by(Genero) |>
  rstatix::get_summary_stats(Temperatura, type = "common")

print(desc_tbl)

# Boxplot simples (janela gráfica não aparece em VS Code; use ggsave depois)
boxplot(ex1_aula2$Temperatura ~ ex1_aula2$Genero,
        ylab = "Temperatura (ºC)", xlab = "Gênero")

#%% 🇷 Teste de pressupostos (Shapiro, Levene, QQPlot)
%%R
# Normalidade por grupo
shapiro_tbl <- ex1_aula2 |>
  dplyr::group_by(Genero) |>
  rstatix::shapiro_test(Temperatura)
print(shapiro_tbl)

# QQ-plot por grupos (abre device gráfico; melhor salvar depois com ggplot)
car::qqPlot(x = ex1_aula2$Temperatura, groups = ex1_aula2$Genero)

# Homogeneidade de variâncias
lev_tbl <- rstatix::levene_test(data = ex1_aula2, Temperatura ~ Genero, center = "mean")
print(lev_tbl)

#%% 🇷 Teste t, tamanho de efeito e estatística não-padronizada
%%R
# Teste t com variâncias iguais (igual ao seu código)
tt <- t.test(Temperatura ~ Genero, data = ex1_aula2,
             alternative = "two.sided", var.equal = TRUE)
print(tt)

# d de Cohen
d_tbl <- effectsize::cohens_d(Temperatura ~ Genero, data = ex1_aula2, paired = FALSE)
print(d_tbl)

# Interpretações de referência
print(effectsize::interpret_cohens_d(0.40, rules = "cohen1988"))
print(effectsize::interpret_cohens_d(0.40, rules = "sawilowsky2009"))

# Não-padronizado: média e desvio
mean_sd_tbl <- ex1_aula2 |>
  dplyr::group_by(Genero) |>
  rstatix::get_summary_stats(Temperatura, type = "mean_sd") |>
  as.data.frame()
print(mean_sd_tbl)

# Diferença de médias (exemplo do seu código)
# Ajuste os valores caso queira fixos; aqui calculo a partir do dataset:
m_by_group <- ex1_aula2 |>
  dplyr::group_by(Genero) |>
  dplyr::summarise(mean_T = mean(Temperatura), .groups="drop")

if (nrow(m_by_group) == 2) {
  dif <- diff(m_by_group$mean_T)  # segunda - primeira (ordem alfabética dos níveis)
  print(paste("Diferença de médias (ordem dos níveis):", round(dif, 3)))
}

#%% 🇷 Gráfico (dotplot) + ggsignif e salvar PNG
%%R
# Para o ggsignif, pegamos os dois níveis existentes
grps <- as.character(levels(ex1_aula2$Genero))
if (length(grps) >= 2) {
  comp <- list(grps[1:2])
} else {
  comp <- NULL
}

p <- ggplot(data = ex1_aula2, aes(x = Genero, y = Temperatura)) +
  ggbeeswarm::geom_beeswarm(method = "center",
                            color = "cadetblue",
                            alpha = 0.7, cex = 4) +
  geom_crossbar(stat = "summary", fun = "mean", fatten = 1,
                width = 0.5) +
  geom_errorbar(stat = "summary", fun.data = "mean_sd", width = 0.15) +
  (if (!is.null(comp)) ggsignif::geom_signif(comparisons = comp,
                                            annotations = "*", vjust = 0.5,
                                            textsize = 5, tip_length = 0.01) else NULL) +
  scale_y_continuous(labels = scales::number_format(decimal.mark = ",")) +
  labs(y = "Temperatura (ºC)", x = "Gênero") +
  theme_classic()

print(p)
ggsave("dotplot.png", plot = p, dpi = 600, width = 3.5, height = 3.5)

# Garantias mínimas
ex1_aula2 <- ex1_aula2[!is.na(ex1_aula2$Genero) & !is.na(ex1_aula2$Temperatura), ]
ex1_aula2$Genero <- droplevels(factor(ex1_aula2$Genero))

if (length(levels(ex1_aula2$Genero)) != 2) {
  stop(sprintf("Genero precisa ter exatamente 2 níveis. Níveis atuais: %s",
               paste(levels(ex1_aula2$Genero), collapse=", ")))
}

# t-test independente (variâncias iguais, como no seu código)
resultado <- t.test(Temperatura ~ Genero, data = ex1_aula2,
                    alternative = "two.sided", var.equal = TRUE)

# Report: imprime o objeto (sem usar cat)
rep_obj <- report::report(resultado)
print(rep_obj)



#%% ⬅️ Exportar objetos do R → Python
%%R -o desc_tbl -o shapiro_tbl -o lev_tbl -o d_tbl -o rep_txt -o ex1_aula2
invisible(NULL)  # corpo R “vazio” só pra célula ser válida

#%% 🐍 Ver no Python o que voltou
type(desc_tbl), desc_tbl.head()
type(shapiro_tbl), shapiro_tbl
type(lev_tbl), lev_tbl
type(d_tbl), d_tbl
print("\nReport (texto):\n", rep_txt)
ex1_aula2.head()

# %%
