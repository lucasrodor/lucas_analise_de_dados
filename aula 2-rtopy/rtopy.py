#%% 🔧 Bootstrap (execute esta célula primeiro)
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "pt_BR.UTF-8"
os.environ["LC_ALL"] = "pt_BR.UTF-8"
# Se precisar apontar o R manualmente no Windows, descomente e ajuste:
# os.environ["R_HOME"] = r"C:\Program Files\R\R-4.4.1"
# os.environ["PATH"]  = r"C:\Program Files\R\R-4.4.1\bin\x64;" + os.environ["PATH"]

# Carrega os magics do R no ipykernel atual
get_ipython().run_line_magic("load_ext", "rpy2.ipython")
print("Extensão %R carregada.")

#%% 🐍 [PYTHON] Carregar CSV e preparar DataFrame
import pandas as pd
pd.options.display.float_format = "{:.2f}".format

# >>> AJUSTE O CAMINHO AQUI <<<
csv_path = r"C:\Lucas\IBMEC\4 Semestre\Inferencia estatística\Aula 2\Data\normtemp.csv"

# Lê usando ';' como separador
df_py = pd.read_csv(csv_path, sep=';')

# Normaliza nomes: sem acentos, minúsculo, sem espaços extras
orig_cols = df_py.columns.tolist()
df_py.columns = (
    df_py.columns
      .str.normalize('NFKD').str.encode('ascii','ignore').str.decode('ascii')
      .str.strip().str.lower()
)

# Detecta colunas-alvo (gênero/temperatura) por aliases comuns
alvo_genero_alias = {"genero","genero.","sexo","sex","gender"}
alvo_temp_alias   = {"temperatura","temp","temperature","bodytemp","body_temp","body.temperature"}

col_genero = next((c for c in df_py.columns if c in alvo_genero_alias), None)
col_temp   = next((c for c in df_py.columns if c in alvo_temp_alias), None)

if col_genero is None or col_temp is None:
    raise ValueError(
        f"Não achei as colunas de Gênero/Temperatura.\n"
        f"Colunas do arquivo: {orig_cols}\n"
        f"Detectado genero={col_genero}, temperatura={col_temp}"
    )

# Renomeia para os nomes esperados no R
df_py = df_py.rename(columns={col_genero: "Genero", col_temp: "Temperatura"})

# Converte Temperatura (suporta vírgula), arredonda
df_py["Temperatura"] = (
    df_py["Temperatura"].astype(str).str.replace(",", ".", regex=False).astype(float).round(2)
)
# Gênero como string “limpa”
df_py["Genero"] = df_py["Genero"].astype(str).str.strip()

# Remove NAs críticos
df_py = df_py.dropna(subset=["Genero","Temperatura"]).reset_index(drop=True)

print("Prévia do DataFrame (Python):")
print(df_py.head())
print("Shape:", df_py.shape)

#%% 📦 🇷 Pacotes (rode 1x por ambiente)
%%R
options(repos = c(CRAN = "https://cloud.r-project.org"))
if (!require("pacman")) install.packages("pacman", quiet=TRUE)
pacman::p_load(dplyr, rstatix, ggplot2, ggpubr, ggsignif,
               effectsize, ggbeeswarm, report, car, scales)

#%% 🇷 Recomputar tudo no R e EXPORTAR para o Python (idempotente)
%%R -i df_py -o desc_tbl -o shapiro_tbl -o lev_tbl -o d_tbl -o rep_txt -o ex1_aula2
# 1) Dataset base
ex1_aula2 <- df_py
ex1_aula2 <- ex1_aula2[!is.na(ex1_aula2$Genero) & !is.na(ex1_aula2$Temperatura), ]
ex1_aula2$Genero <- droplevels(factor(ex1_aula2$Genero))

# 2) Descritivo e pressupostos
desc_tbl <- ex1_aula2 |>
  dplyr::group_by(Genero) |>
  rstatix::get_summary_stats(Temperatura, type = "common")

shapiro_tbl <- ex1_aula2 |>
  dplyr::group_by(Genero) |>
  rstatix::shapiro_test(Temperatura)

lev_tbl <- rstatix::levene_test(data = ex1_aula2, Temperatura ~ Genero, center = "mean")

# 3) t-test + d de Cohen + report()
if (length(levels(ex1_aula2$Genero)) == 2) {
  tt <- t.test(Temperatura ~ Genero, data = ex1_aula2,
               alternative = "two.sided", var.equal = TRUE)
  d_tbl <- effectsize::cohens_d(Temperatura ~ Genero, data = ex1_aula2, paired = FALSE)

  rep_obj <- report::report(tt)
  rep_txt <- paste(capture.output(print(rep_obj)), collapse = "\n")
} else {
  d_tbl   <- data.frame()
  rep_txt <- sprintf("Genero precisa ter exatamente 2 níveis. Níveis atuais: %s",
                     paste(levels(ex1_aula2$Genero), collapse = ", "))
}

invisible(NULL)

#%% 🐍 Ver o que voltou do R
print("\n==== REPORT (R/report) ====\n")
print(rep_txt)

print("\n[desc_tbl]\n", desc_tbl.head())
print("\n[shapiro_tbl]\n", shapiro_tbl)
print("\n[lev_tbl]\n", lev_tbl)
print("\n[d_tbl]\n", d_tbl)
print("\n[Amostra ex1_aula2]\n", ex1_aula2.head())

#%% 🇷 Gráfico (dotplot) + ggsignif e salvar PNG
%%R
grps <- levels(ex1_aula2$Genero)
comp <- if (length(grps) >= 2) list(grps[1:2]) else NULL

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
cat("Gráfico salvo em: dotplot.png\n")

# %%
