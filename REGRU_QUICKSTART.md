# Быстрый старт на REG.RU - Пошаговая инструкция

## Что вам понадобится

- ✅ Домен guestreviews.ru (куплен на REG.RU)
- ✅ VPS/VDS хостинг на REG.RU (минимум 2GB RAM)
- ✅ Доступ к панели управления REG.RU

## Шаг 1: Получите данные VPS (2 минуты)

1. Войдите на https://www.reg.ru/
2. Перейдите в "Мои услуги" → "VPS"
3. Запишите:
   ```
   IP адрес: _________________
   Логин: root
   Пароль: _________________ (из письма или панели)
   ```

## Шаг 2: Настройте DNS (3 минуты)

1. В панели REG.RU перейдите в "Домены"
2. Нажмите на guestreviews.ru
3. Выберите "Управление DNS" или "DNS-серверы и зона"
4. Добавьте/измените записи:

```
Тип    Имя (поддомен)    Значение (IP адрес)
A      @                 ВАШ_IP_VPS
A      www               ВАШ_IP_VPS
```

5. Нажмите "Сохранить"
6. ⏰ Подождите 5-30 минут для применения

## Шаг 3: Подключитесь к серверу (2 минуты)

### Windows

**Вариант A: PowerShell (встроенный)**
```powershell
ssh root@ВАШ_IP_VPS
# Введите пароль
```

**Вариант B: PuTTY (если PowerShell не работает)**
1. Скачайте PuTTY: https://www.putty.org/
2. Запустите PuTTY
3. Host Name: ВАШ_IP_VPS
4. Port: 22
5. Нажмите "Open"
6. Login: root
7. Password: ваш_пароль

## Шаг 4: Загрузите проект на сервер (5 минут)

### Вариант A: Через Git (если код в репозитории)

```bash
# На сервере
mkdir -p /opt/hotel-reviews
cd /opt/hotel-reviews
git clone https://github.com/YOUR_USERNAME/hotel-guest-reviews.git .
```

### Вариант B: Через FileZilla (рекомендуется для начинающих)

1. **Скачайте FileZilla**: https://filezilla-project.org/
2. **Подключитесь**:
   - Файл → Менеджер сайтов → Новый сайт
   - Протокол: SFTP
   - Хост: ВАШ_IP_VPS
   - Порт: 22
   - Тип входа: Нормальный
   - Пользователь: root
   - Пароль: ваш_пароль
   - Нажмите "Соединиться"

3. **Создайте папку на сервере**:
   - В правой панели (сервер) перейдите в /opt/
   - Правый клик → Создать каталог → hotel-reviews
   - Зайдите в /opt/hotel-reviews/

4. **Загрузите файлы**:
   - В левой панели (ваш компьютер) найдите папку с проектом
   - Выделите все файлы
   - Перетащите в правую панель (сервер)
   - Дождитесь окончания загрузки

### Вариант C: Через SCP (для продвинутых)

```powershell
# На вашем компьютере (Windows PowerShell)
scp -r C:\путь\к\hotel-guest-reviews\* root@ВАШ_IP_VPS:/opt/hotel-reviews/
```

## Шаг 5: Автоматическое развертывание (5 минут)

```bash
# На сервере (в SSH/PuTTY)
cd /opt/hotel-reviews

# Сделать скрипт исполняемым
chmod +x scripts/deploy.sh

# Запустить автоматическое развертывание
bash scripts/deploy.sh
```

Скрипт спросит:
1. **Редактировать .env?** → Нажмите Enter, измените пароли, сохраните (Ctrl+O, Enter, Ctrl+X)
2. **Получить SSL сертификат?** → Введите `y` и нажмите Enter
3. **Создать тестовые данные?** → Введите `y` и нажмите Enter

## Шаг 6: Проверка (1 минута)

Откройте в браузере:
- ✅ https://guestreviews.ru
- ✅ https://guestreviews.ru/api/v1/docs

Если открывается - **поздравляю, готово!** 🎉

## Что делать, если не работает?

### DNS еще не обновился

```bash
# Проверить DNS
dig guestreviews.ru +short
# Должен вернуть IP вашего VPS
```

Если возвращает другой IP или ничего:
- Подождите еще 10-20 минут
- Проверьте настройки DNS в панели REG.RU

### Ошибка при получении SSL

```bash
# Проверить, что DNS настроен
dig guestreviews.ru +short

# Попробовать еще раз
cd /opt/hotel-reviews
bash scripts/setup_ssl.sh
```

### Сайт не открывается

```bash
# Проверить статус
cd /opt/hotel-reviews
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапустить
docker-compose -f docker-compose.prod.yml restart
```

## Тестовые учетные данные

После развертывания войдите:
- **Владелец**: admin@grandhotel.ru / admin123
- **Менеджер**: manager@grandhotel.ru / manager123

⚠️ **Важно**: Измените эти пароли после первого входа!

## Полезные команды

```bash
# Перейти в папку проекта
cd /opt/hotel-reviews

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапустить
docker-compose -f docker-compose.prod.yml restart

# Остановить
docker-compose -f docker-compose.prod.yml down

# Запустить снова
docker-compose -f docker-compose.prod.yml up -d
```

## Следующие шаги

1. ✅ Войдите в систему: https://guestreviews.ru/api/v1/docs
2. ✅ Измените пароли тестовых пользователей
3. ✅ Создайте свой отель
4. ✅ Добавьте пользователей
5. ✅ Настройте интеграции

## Нужна помощь?

### Техподдержка REG.RU
- Сайт: https://www.reg.ru/support/
- Телефон: 8 (800) 505-42-85
- Email: support@reg.ru

### Документация проекта
- Полная инструкция: [REGRU_SETUP.md](REGRU_SETUP.md)
- FAQ: [FAQ.md](FAQ.md)
- API документация: https://guestreviews.ru/api/v1/docs

## Видео-инструкция (если нужна)

Если нужна видео-инструкция, могу создать скринкаст с записью всех шагов.

---

**Время развертывания**: ~15-20 минут
**Сложность**: Легко (следуйте инструкциям)
**Результат**: Работающий сайт на https://guestreviews.ru
