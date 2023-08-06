# Boston Housing package

## Общая информация

Данный проект представляет собой пакет Python, предназначенный для работы с данными о жилой недвижимости в Бостоне, который может быть использован для изучения структуры ML моделей, задействованных в Production сфере.

## Структура кода 
### Configs

Параметры модели задаются через configs. Конфиги представлены файлами yaml. Ценности для параметров можно установить в файле `bhousing_model/config.yml`. Configs анализируются и проверяются в `bhousing_model/config/core.py` модуль, использующий библиотеку [StrictYaml](https://github.com/crdoconnor/strictyaml) для разбора и [Pydantic](https://pydantic-docs.helpmanual.io/) для проверки типов значений. 

## Настройка пайплайна и обучение

Pipeline установлен в bhousing_model/pipeline.pyфайл. Обучение проходит в файле `bhousing_model/train_pipeline.py`. Все этапы обработки данных выполняются в [Scikit-learn](https://scikit-learn.org/stable/), включая пользовательские преобразования, хранящиеся в файле `bhousing_model/processing/features.py`. 


### Как делать прогнозы

Код для предсказания устанавливается из файла `bhousing_model/predict.py`. Перед каждым предсказанием производится проверка входных данных. Код для проверки можно найти в файле `bhousing_model/processing/validation.py`. 


## Как запустить код 

Код можно запустить с помощью инструмента [Tox](https://pypi.org/project/tox/). Tox — это удобный способ автоматической настройки среды и путей Python и запуска необходимых команд из командной строки. Файл с описанием tox можно найти в файле `tox.ini`. Следующие команды можно запустить из командной строки используя Tox:

* Запустить обучение: сначала создайте каталог для сохранения моделей, если такового нет `mkdir ./bhousing_model/trained_models`, а затем запустите `tox -e train`
* Запустить тестирование (через [pytest](https://docs.pytest.org/en/6.2.x/)): `tox -e test_package`
* Запустить проверку типов (через [mypy](https://mypy.readthedocs.io/en/stable/)): `tox -e typechecks`
* Запустить проверку стиля (через [black](https://github.com/psf/black), [isort](https://github.com/PyCQA/isort), [mypy](https://mypy.readthedocs.io/en/stable/)
и [flake8](https://pypi.org/project/flake8/)): `tox -e stylechecks`

## Как установить пакет

Для установки пакета запустите 

```
pip install bhousing-model
```

После этого вы можете делать прогнозы, используя пакет: 

```
from bhousing_model.predict import make_prediction

# Пример входных данных
input_dict = {'ID': [7], 'CRIM': [0.08829], 'INDUS': [7.87], 'CHAS': [0.0], 
              'NOX': [0.524], 'RM': [6.012], 'AGE': [66.6], 'DIS': [5.5605], 'RAD': [5.0], 
              'TAX': [311.0], 'PTRATIO': [15.2], 'B': [395.6], 'LSTAT': [12.43]}

result = make_prediction(input_data=input_dict)

print(result)
```
