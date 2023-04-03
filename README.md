## Руководство по использованию консольного клиента анализатора стоков

Этот Python-скрипт предоставляет интерфейс командной 
строки (CLI) для взаимодействия с сенсором сточных вод, 
подключенным к последовательному порту через плату-адаптер.  

Адрес репозитория с прошивкой: https://github.com/houseofbigseals/muddy_water_firmware  

Адрес репозитория со схематикой:https://github.com/houseofbigseals/muddy_water_sensor  

Клиент реализован с использованием пакета click и позволяет отправлять 
команды на устройство-сенсор, получать ответы в формате
JSON и парсить их.   
Он предоставляет несколько команд, которые позволяют 
выполнять различные операции с устройством, такие как 
получение данных о температуре и спектре, установка 
состояния светодиода и измерение данных в течение 
определенного времени.  

***NB!*** *По умолчанию подразумевается что вы будете использовать 
этот клиент только на Линуксе.*

### Установка

Для использования этого клиента вам нужно установить 
Python 3.x на ваш компьютер. Также вам нужно установить 
пакеты click и pyserial. 
Вы можете сделать это, запустив следующие команды:
```commandline
python3 -m pip install click
python3 -m pip install pyserial
```



### Использование
### Отладочные команды

Сначала перечислим отладочные команды, которые выводят 
результаты своей работы в консоль, а не в csv-файл.

1.  get_temp

Эта команда получает данные о температуре с устройства. Вы можете использовать флаг -v или --verbose, чтобы отобразить дополнительную информацию. Например:
```
python3 mw_client.py get_temp -v
```

2.  get_status

Эта команда получает информацию об устройстве. 
Вы можете использовать флаг -v или --verbose, 
чтобы отобразить дополнительную информацию. Например:
```
python3 mw_client.py get_status -v
```
эта команда выдает в ответ много загадочных полей, где:   

```
    ["mem"] = freeRam();  - объем свободной памяти ардуины 
    ["asst"] = sensor.getStatus();  - статус состояния спектрометра, должен быть 106 если все ок
    ["devt"] = sensor.getDevType(); - тип спектрометра
    ["hvv"] = sensor.getHWVersion();  - версия железа спектрометра
    ["fwmv"] = sensor.getFWMajorVersion(); - версия прошивки спектрометра
    ["fwpv"] = sensor.getFWPatchVersion();
    ["fwbv"] = sensor.getFWBuildVersion();
    ["temp0"] = sensor.getTemperature(0); - температура трех чипов на плате спектрометра
    ["temp1"] = sensor.getTemperature(1);
    ["temp2"] = sensor.getTemperature(2);
    ["dsaddr"] - уникальный номер сенсора температуры ds18b20 
```
Она нужна в основном чтобы проверить что спектрометр и термометр живы.

3.  get_spectrum

Эта команда получает данные спектра с устройства.
Вы можете использовать флаг -v или --verbose,
чтобы отобразить дополнительную информацию. Например:

```
python3 mw_client.py get_spectrum -v
```

4. set_led

Эта команда устанавливает состояние светодиода на 
устройстве. Вы можете указать тип светодиода, 
используя опцию -l и значение состояния,
используя опцию -s. 

- -l тип светодиода, ['test', 'uv', 'ir', 'white']
- -s состояние 0 или 1

Светодиод 'test' - это светодиод самой ардуины. нужен на всякий случай,
для отладки протокола.

Вы можете также 
использовать флаг -v или --verbose, чтобы 
отобразить дополнительную информацию. Например:

```
python3 mw_client.py mw set_led -l white -s 1 -v
```


Эта команда устанавливает белый светодиод 
в состояние "включено" и отображает
дополнительную информацию.

### Основные команды

5.  measure

Эта команда измеряет спектры для __одного__ выбранного светодиода 
в течение определенного времени.  
 
- -l тип светодиода, ['test', 'uv', 'ir', 'white']
- -mi (measure interval) интервал измерения, 
- -si (sleep interval) интервал ожидания после измерения,
- -n  количество измерений,
- -p путь к csv-файлу вывода

***NB!*** Времена -mi и -si  не могут быть меньше 1 секунды, это связано
с особенностями протокола управления сенсором.

Вы можете также использовать
флаг -v или --verbose, чтобы отобразить дополнительную
информацию. Например:

```
python3 mw_client.py measure -l white -mi 3 -si 1 -n 5 -p data.csv -v
```
Эта команда измеряет данные для белого светодиода в 
течение 3 секунд, ожидает 1 секунду, выполняет 5 подобных
измерений и сохраняет результаты в файл CSV с именем data.csv.

Если путь -p не указан, то результаты будут выведены в консоль.

6. series_measure

Эта команда измеряет данные для **всех трех** светодиодов 
в течение определенного времени.

- -mi (measure interval) интервал измерения, 
- -si (sleep interval) интервал ожидания после измерения,
- -n  количество измерений,
- -p путь к csv-файлу вывода

***NB!*** Времена -mi и -si  не могут быть меньше 1 секунды, это связано
с особенностями протокола управления сенсором.

Вы можете также использовать
флаг -v или --verbose, чтобы отобразить дополнительную
информацию. Например:

```
python3 mw_client.py series_measure -mi 3 -si 1 -n 5 -p data.csv -v
```

Эта команда измеряет данные для всех трех светодиодов 
в течение 3 секунд, ожидает 1 секунды, выполняет 5 
измерений и сохраняет результаты в файл CSV с именем data.csv.

Если путь -p не указан, то результаты будут выведены в консоль.

### Формат csv-файла

Поля разделены запятыми.  
Каждое измерение от конкретного светодиода пишется в отдельную строку.   
Колонки такие:  
```
Дата, время, температура, время измерения, время паузы, тип светодиода, 610, 680, 730, 760, 810, 860, 560, 585, 645, 705, 900,
 940, 410, 435, 460, 485, 510, 535
```
Числа - частоты, на которых измерял спектрометр, взяты из примера к прошивке uray.
### Выбор порта

Плата-сенсор имеет драйвер ch340g, поэтому по 
умолчанию скрипт будет подключаться к порту:
```
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0
```

Если по какой-то причине скрипт не может найти последовательный
порт (например потому что вы заменили ардуину на плате адаптера), куда подключена плата-адаптер, то надо его найти 
самостоятельно.

```commandline
ls /dev/serial/by-id/
```

Это должно отобразить список всех последовательных 
портов в вашей системе.

```commandline
python mw_client.py --port <путь_к_последовательному_порту> some_command --params params
```

Замените <путь_к_последовательному_порту> на путь
к последовательному порту, к которому подключено 
устройство.  
Надо будет указывать этот путь скрипту в каждой команде 
после параметра --port.
