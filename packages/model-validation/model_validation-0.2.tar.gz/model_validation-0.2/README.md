# Model Validation

![Python versions](https://img.shields.io/pypi/pyversions/model-validation)
[![GitHub Issues](https://img.shields.io/github/issues/Alexandre-Papandrea/model_validation)](https://github.com/Alexandre-Papandrea/model_validation/issues)
[![License](https://img.shields.io/github/license/Alexandre-Papandrea/model_validation)](https://github.com/Alexandre-Papandrea/model_validation/blob/main/LICENSE)

`model_validation` é uma biblioteca Python projetada para tornar a validação de modelos de Machine Learning mais acessível e eficiente. Com um conjunto abrangente de gráficos e métricas, esta biblioteca ajuda a simplificar e acelerar a etapa de validação do pipeline de Machine Learning.

## 🛠️ Instalação

Você pode instalar a biblioteca `model_validation` via pip:

\`\`\`shell
pip install model_validation
\`\`\`

## 🚀 Uso

Primeiro, importe a função `plots_regressao` de `model_validation`:

\`\`\`python
from model_validation import plots_regressao
\`\`\`

Depois, chame a função `plots_regressao` passando o modelo, os dados de teste e o valor verdadeiro como argumentos:

\`\`\`python
plots_regressao(model, X_test, y_test)
\`\`\`

## 🧪 Testes

Para rodar os testes, use o seguinte comando:

\`\`\`shell
pytest
\`\`\`

## 🤝 Contribuição

Agradecemos todas as contribuições, seja corrigindo bugs, adicionando novos recursos ou melhorando a documentação. Aqui estão algumas diretrizes:

1. Faça um fork do repositório e crie uma nova branch.
2. Faça suas alterações na nova branch.
3. Rode os testes para garantir que suas alterações não quebrem nada.
4. Faça um pull request descrevendo suas alterações. 

Se você tiver alguma dúvida ou sugestão, sinta-se à vontade para abrir uma issue.

## 👥 Mantenedores

- [Alexandre Papandrea](https://github.com/Alexandre-Papandrea)

## 📜 Licença

`model_validation` é licenciado sob os termos da [MIT License](LICENSE).
