#!/usr/bin/env python3
"""Publish the canonical Georivo SEO money pages through Blog Core.

This migration is deterministic and idempotent. It creates/updates the Blog Core
jobs, localization rows, audit log, and native published records for site 14.
"""

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SITE_ID = 14
LANGUAGES = ("en", "de", "es", "fr", "ru")
BLOG_CORE_ORIGIN = "https://blog.yas.ooo"
PUBLISHED_AT = "2026-07-25T00:00:00+00:00"

HEROES = {
    "how-it-works": "/sites/14/article-assets/9c9d80f8c5ede189f69aae04/property-showcase-hero.jpg",
    "coverage": "/sites/14/article-assets/8d6269b60ac5ba252fe43e7f/aerial-view-hero.jpg",
    "pricing": "/sites/14/article-assets/bdc2dce5524c72ca1ab41c29/hero-add-3d-map-real-estate.jpg",
}

PAGES = {
    "how-it-works": {
        "en": {
            "title": "How Georivo Creates a 3D Property Flyover",
            "description": "See how Georivo turns a supported property address into a guided, interactive 3D flyover and embeds it on a real estate listing website.",
            "category": "How Georivo works",
            "lead": "One confirmed property address becomes a guided location story: Georivo checks real 3D coverage, plans the camera route, previews the result and publishes a protected, explorable widget.",
            "sections": [
                ("Confirm the exact property", "Enter a complete street address and choose the correct Google suggestion. If an address resolves ambiguously, use the map to correct the building. The confirmed latitude and longitude remain the authoritative camera target; Georivo does not silently replace them with a driveway, parcel centroid or nearby parking area."),
                ("Verify real 3D coverage", "The server resolves the point and checks the configured provider. Supported, partial, unavailable, regionally unsupported and technical-error outcomes are separate states. A provider outage, invalid key or billing problem is never converted into a false claim that the property itself lacks coverage."),
                ("Choose the location story", "Property Showcase approaches the property and finishes with an orbit. Neighborhood Story visits selected nearby places before arriving at the property. Arrival Guide starts from a transport or parking point and moves toward the destination. Automatically suggested places remain editable."),
                ("Direct the camera", "Choose Auto, Zoom, Orbit, Point to Point or Spiral, then set landscape or vertical format, duration, closest distance and camera angle. The settings change the live camera choreography; they are not decorative controls."),
                ("Preview before publishing", "The free preview loads a live Google Maps 3D scene only after Play. The visitor can inspect the result at the selected address before paying. Texture quality and local geometry remain provider-, location-, device- and network-dependent, so the live scene is the final visual check."),
                ("Publish, embed and control", "A paid account publishes an opaque share link and a responsive iframe restricted to an authorized domain. The dashboard keeps the saved configuration, usage and status in one place. Revoking pauses public access without deleting the project; restoring makes it available again while the subscription and usage allowance permit it."),
            ],
            "faqs": [
                ("Is Georivo recorded drone footage?", "No. It is an interactive geospatial 3D visualization with a programmed virtual camera."),
                ("Does every address work?", "No. Coverage and visual quality depend on the provider and the exact location. Check the address before publishing."),
                ("Can a visitor explore after playback?", "Yes. After the guided route finishes, the live scene remains interactive."),
                ("Do ordinary page views count as plays?", "No. A play is counted only when a visitor starts the live 3D experience."),
            ],
            "finalTitle": "Check a property, shape the story and preview the real route.",
            "cta": "Check a property address",
        },
        "de": {
            "title": "So erstellt Georivo einen 3D-Immobilienflug",
            "description": "Erfahren Sie, wie Georivo aus einer unterstützten Adresse eine geführte, interaktive 3D-Standortgeschichte für Immobilien-Websites erstellt.",
            "category": "So funktioniert Georivo",
            "lead": "Aus einer bestätigten Adresse wird eine geführte Standortgeschichte: Abdeckung prüfen, Route gestalten, Vorschau ansehen und als geschütztes Widget veröffentlichen.",
            "sections": [
                ("Exakte Immobilie bestätigen", "Geben Sie die vollständige Adresse ein und wählen Sie den richtigen Google-Vorschlag. Bei Unklarheit korrigieren Sie das Gebäude auf der Karte. Die bestätigten Koordinaten bleiben das Kameraziel."),
                ("Echte 3D-Abdeckung prüfen", "Unterstützt, teilweise unterstützt, nicht verfügbar, regional ausgeschlossen und technische Fehler sind getrennte Ergebnisse. Ein Anbieterfehler wird niemals als fehlende Abdeckung ausgegeben."),
                ("Standortgeschichte wählen", "Property Showcase, Neighborhood Story und Arrival Guide beantworten unterschiedliche Käuferfragen. Automatisch vorgeschlagene Orte bleiben editierbar."),
                ("Kamera und Format festlegen", "Bewegung, Hoch- oder Querformat, Dauer, Distanz und Winkel bestimmen die echte Kameraführung der Live-Szene."),
                ("Vor Veröffentlichung prüfen", "Die kostenlose Vorschau lädt Google Maps 3D erst nach Play. Lokale Detailqualität hängt von Ort, Anbieter, Gerät und Netzwerk ab."),
                ("Veröffentlichen und kontrollieren", "Ein bezahltes Konto erstellt einen geschützten Link und ein domaingebundenes iframe. Projekte können widerrufen und später wieder aktiviert werden."),
            ],
            "faqs": [
                ("Ist das eine Drohnenaufnahme?", "Nein. Es ist eine interaktive 3D-Geodatenvisualisierung."),
                ("Funktioniert jede Adresse?", "Nein. Prüfen Sie zuerst die reale Abdeckung und Vorschau."),
                ("Bleibt die Szene interaktiv?", "Ja. Nach der Route kann der Besucher die Umgebung erkunden."),
                ("Zählen normale Seitenaufrufe?", "Nein. Nur ein gestartetes Live-3D zählt als Wiedergabe."),
            ],
            "finalTitle": "Immobilie prüfen, Geschichte gestalten und echte Route ansehen.",
            "cta": "Immobilienadresse prüfen",
        },
        "es": {
            "title": "Cómo crea Georivo un vuelo 3D de una propiedad",
            "description": "Descubre cómo Georivo convierte una dirección compatible en una historia de ubicación 3D guiada e interactiva para una web inmobiliaria.",
            "category": "Cómo funciona Georivo",
            "lead": "Una dirección confirmada se convierte en una historia guiada: cobertura real, ruta de cámara, vista previa y widget protegido.",
            "sections": [
                ("Confirma la propiedad exacta", "Introduce la dirección completa y elige la sugerencia correcta de Google. Si es ambigua, corrige el edificio en el mapa. Las coordenadas confirmadas siguen siendo el objetivo."),
                ("Comprueba cobertura 3D real", "Compatible, parcial, no disponible, región no compatible y error técnico son estados diferentes. Un fallo del proveedor nunca se presenta como falta de cobertura."),
                ("Elige la historia", "Property Showcase, Neighborhood Story y Arrival Guide responden a necesidades distintas. Los lugares sugeridos se pueden editar."),
                ("Configura la cámara", "Movimiento, formato, duración, distancia y ángulo controlan la cámara real de la escena."),
                ("Revisa antes de publicar", "La vista previa gratuita carga Google Maps 3D solo después de Play. El detalle depende del lugar, proveedor, dispositivo y red."),
                ("Publica y controla", "La cuenta de pago crea un enlace protegido y un iframe limitado al dominio autorizado. El panel permite revocar y restaurar el proyecto."),
            ],
            "faqs": [
                ("¿Es vídeo de dron?", "No. Es una visualización geoespacial 3D interactiva."),
                ("¿Funciona cualquier dirección?", "No. Hay que comprobar la cobertura y la vista previa reales."),
                ("¿Se puede explorar después?", "Sí. La escena sigue siendo interactiva al terminar la ruta."),
                ("¿Cuentan las visitas normales?", "No. Solo cuenta cuando el visitante inicia el 3D."),
            ],
            "finalTitle": "Comprueba la propiedad, diseña la historia y revisa la ruta real.",
            "cta": "Comprobar una dirección",
        },
        "fr": {
            "title": "Comment Georivo crée un survol 3D immobilier",
            "description": "Découvrez comment Georivo transforme une adresse prise en charge en récit de localisation 3D guidé et interactif pour un site immobilier.",
            "category": "Fonctionnement de Georivo",
            "lead": "Une adresse confirmée devient un récit guidé : couverture réelle, parcours caméra, aperçu puis widget protégé.",
            "sections": [
                ("Confirmer le bien exact", "Saisissez l’adresse complète et choisissez la bonne suggestion Google. En cas d’ambiguïté, corrigez le bâtiment sur la carte. Les coordonnées confirmées restent la cible."),
                ("Vérifier la couverture 3D", "Pris en charge, partiel, indisponible, région non prise en charge et erreur technique sont des états distincts. Une panne fournisseur n’est jamais présentée comme une absence de couverture."),
                ("Choisir le récit", "Property Showcase, Neighborhood Story et Arrival Guide répondent à des besoins différents. Les lieux suggérés restent modifiables."),
                ("Régler la caméra", "Mouvement, format, durée, distance et angle contrôlent réellement la caméra de la scène."),
                ("Prévisualiser avant publication", "L’aperçu gratuit ne charge Google Maps 3D qu’après Play. Le détail dépend du lieu, du fournisseur, de l’appareil et du réseau."),
                ("Publier et contrôler", "Le compte payant crée un lien protégé et un iframe limité au domaine autorisé. Le tableau de bord permet de révoquer et restaurer le projet."),
            ],
            "faqs": [
                ("Est-ce une vidéo drone ?", "Non. Il s’agit d’une visualisation géospatiale 3D interactive."),
                ("Toutes les adresses fonctionnent-elles ?", "Non. La couverture et l’aperçu doivent être vérifiés."),
                ("Peut-on explorer après le parcours ?", "Oui. La scène reste interactive."),
                ("Les simples pages vues comptent-elles ?", "Non. Seul le démarrage du 3D compte."),
            ],
            "finalTitle": "Vérifiez le bien, composez le récit et examinez le parcours réel.",
            "cta": "Vérifier une adresse",
        },
        "ru": {
            "title": "Как Georivo создаёт 3D-пролёт объекта недвижимости",
            "description": "Посмотрите, как Georivo превращает поддерживаемый адрес в управляемую интерактивную 3D-историю локации для сайта недвижимости.",
            "category": "Как работает Georivo",
            "lead": "Один подтверждённый адрес превращается в управляемую историю локации: реальная проверка покрытия, маршрут камеры, превью и защищённый виджет.",
            "sections": [
                ("Подтвердите точный объект", "Введите полный адрес и выберите правильную подсказку Google. Если адрес неоднозначный, исправьте здание на карте. Подтверждённые координаты остаются целью камеры."),
                ("Проверьте реальное 3D-покрытие", "Поддерживается, частично поддерживается, недоступно, неподдерживаемый регион и техническая ошибка — разные состояния. Ошибка провайдера никогда не выдаётся за отсутствие покрытия."),
                ("Выберите историю", "Показ объекта, История района и Маршрут прибытия отвечают на разные вопросы покупателя. Автоматически предложенные места можно менять."),
                ("Настройте камеру", "Движение, формат, длительность, дистанция и угол действительно управляют камерой живой сцены."),
                ("Проверьте до публикации", "Бесплатное превью загружает Google Maps 3D только после Play. Детализация зависит от места, провайдера, устройства и сети."),
                ("Опубликуйте и управляйте", "Платный аккаунт создаёт защищённую ссылку и iframe для разрешённого домена. Проект можно отозвать и затем восстановить."),
            ],
            "faqs": [
                ("Это съёмка дроном?", "Нет. Это интерактивная геопространственная 3D-визуализация."),
                ("Работает любой адрес?", "Нет. Сначала нужно проверить реальное покрытие и превью."),
                ("Можно исследовать район после пролёта?", "Да. После маршрута сцена остаётся интерактивной."),
                ("Обычные просмотры страницы считаются?", "Нет. Считается только запуск живого 3D."),
            ],
            "finalTitle": "Проверьте объект, настройте историю и посмотрите реальный маршрут.",
            "cta": "Проверить адрес объекта",
        },
    },
    "coverage": {
        "en": {
            "title": "3D Property Map Coverage and Address Check",
            "description": "Check whether an address has suitable 3D map coverage for a Georivo property flyover and understand supported, partial and unavailable results.",
            "category": "3D coverage",
            "lead": "Coverage is checked against real provider data before publication. Georivo does not use a timer, decorative animation or fabricated success response.",
            "sections": [
                ("Supported", "Detailed photorealistic 3D data is available around the confirmed point. The live preview can load, but the visitor should still inspect the exact property because source geometry and texture quality vary by location."),
                ("Partially supported", "The provider has 3D surface data, while close-range local detail may be limited. Georivo keeps the result usable and clearly labelled, recommends a wider camera distance and leaves the final decision to the live preview."),
                ("Unavailable", "The provider does not return sufficient local detail for the selected point. This is a real negative result. The visitor can request a future coverage notification without being forced to create an account."),
                ("Unsupported region", "Product-market policy can exclude a region before tile traversal. This is reported separately from an ordinary uncovered address so the reason remains understandable."),
                ("Technical error", "Invalid credentials, quota, billing, authorization, upstream or network problems are operational failures. They must be retried or fixed; Georivo never converts them into an unsupported-address message."),
                ("Exact-point visual check", "A hierarchy or coverage match proves that provider data reaches the location, not that every roof, tree or façade is equally detailed. The live Google Maps 3D scene remains the practical visual acceptance check."),
            ],
            "faqs": [
                ("Is the result simulated?", "No. The form calls the production coverage endpoint and displays the provider-backed result."),
                ("Why can coverage be partial?", "A provider can have terrain and 3D surface data while close-range building detail remains limited."),
                ("Does a technical error mean the address is unsupported?", "No. It means the provider request could not be completed and should be retried."),
                ("Is the entered address stored in analytics?", "No. Raw addresses and coordinates are excluded from general analytics."),
            ],
            "finalTitle": "Check the exact address before you design or publish the story.",
            "cta": "Check an address",
            "checkerLabel": "Property address",
            "checkerPlaceholder": "Enter a street, city and country",
            "checkerButton": "Check real 3D coverage",
            "checkerNote": "Real provider response · no raw address is sent to analytics",
        },
        "de": {
            "title": "3D-Kartenabdeckung für eine Immobilienadresse prüfen",
            "description": "Prüfen Sie, ob eine Adresse geeignete 3D-Abdeckung für Georivo besitzt, und verstehen Sie volle, teilweise oder fehlende Abdeckung.",
            "category": "3D-Abdeckung",
            "lead": "Die Abdeckung wird vor der Veröffentlichung mit echten Anbieterdaten geprüft. Es gibt keinen simulierten Erfolg.",
            "sections": [
                ("Unterstützt", "Detaillierte fotorealistische 3D-Daten sind am bestätigten Punkt verfügbar. Prüfen Sie dennoch die exakte Immobilie in der Live-Vorschau."),
                ("Teilweise unterstützt", "3D-Oberfläche ist vorhanden, Nahdetails können aber begrenzt sein. Eine größere Kameradistanz wird empfohlen."),
                ("Nicht verfügbar", "Am Punkt fehlen ausreichende lokale Details. Eine Benachrichtigung kann ohne Konto angefordert werden."),
                ("Nicht unterstützte Region", "Eine regionale Produktregel wird getrennt von fehlender lokaler Abdeckung erklärt."),
                ("Technischer Fehler", "Schlüssel-, Quota-, Abrechnungs-, Netzwerk- oder Anbieterprobleme sind keine negative Adressentscheidung."),
                ("Visuelle Prüfung", "Ein Abdeckungstreffer garantiert nicht dieselbe Detailqualität jedes Gebäudes. Die Live-Szene ist die praktische Endkontrolle."),
            ],
            "faqs": [
                ("Ist das Ergebnis simuliert?", "Nein. Das Formular nutzt den produktiven Abdeckungsendpunkt."),
                ("Warum gibt es teilweise Abdeckung?", "Oberfläche kann verfügbar sein, während Gebäudedetails begrenzt sind."),
                ("Ist ein technischer Fehler eine Ablehnung?", "Nein. Die Anfrage muss erneut ausgeführt oder technisch korrigiert werden."),
                ("Speichert Analytics die Adresse?", "Nein. Rohadressen und Koordinaten sind ausgeschlossen."),
            ],
            "finalTitle": "Prüfen Sie die exakte Adresse, bevor Sie die Geschichte veröffentlichen.",
            "cta": "Adresse prüfen",
            "checkerLabel": "Immobilienadresse",
            "checkerPlaceholder": "Straße, Stadt und Land",
            "checkerButton": "Echte 3D-Abdeckung prüfen",
            "checkerNote": "Echte Anbieterantwort · keine Rohadresse in Analytics",
        },
        "es": {
            "title": "Comprueba la cobertura 3D de una propiedad",
            "description": "Comprueba si una dirección tiene cobertura 3D adecuada para Georivo y entiende los resultados compatibles, parciales y no disponibles.",
            "category": "Cobertura 3D",
            "lead": "La cobertura se comprueba con datos reales del proveedor antes de publicar. No existe un éxito simulado.",
            "sections": [
                ("Compatible", "Hay datos 3D fotorrealistas detallados alrededor del punto confirmado. Revisa igualmente la propiedad exacta en vivo."),
                ("Compatibilidad parcial", "Existe superficie 3D, pero el detalle cercano puede ser limitado. Se recomienda más distancia de cámara."),
                ("No disponible", "No hay detalle local suficiente. Se puede solicitar una notificación sin crear cuenta."),
                ("Región no compatible", "La política regional se explica por separado de una dirección sin cobertura."),
                ("Error técnico", "Los fallos de clave, cuota, facturación, red o proveedor no son un resultado negativo de dirección."),
                ("Comprobación visual", "Un resultado de cobertura no garantiza el mismo detalle en todos los edificios. La escena en vivo es la revisión final."),
            ],
            "faqs": [
                ("¿El resultado es simulado?", "No. El formulario llama al endpoint de producción."),
                ("¿Por qué puede ser parcial?", "Puede existir superficie 3D con poco detalle de edificios."),
                ("¿Un error técnico significa no compatible?", "No. La solicitud debe reintentarse o corregirse."),
                ("¿Analytics guarda la dirección?", "No. Las direcciones y coordenadas sin procesar se excluyen."),
            ],
            "finalTitle": "Comprueba la dirección exacta antes de publicar la historia.",
            "cta": "Comprobar dirección",
            "checkerLabel": "Dirección de la propiedad",
            "checkerPlaceholder": "Calle, ciudad y país",
            "checkerButton": "Comprobar cobertura 3D real",
            "checkerNote": "Respuesta real del proveedor · sin dirección en Analytics",
        },
        "fr": {
            "title": "Vérifier la couverture 3D d’une adresse immobilière",
            "description": "Vérifiez si une adresse dispose d’une couverture 3D adaptée à Georivo et comprenez les résultats pris en charge, partiels et indisponibles.",
            "category": "Couverture 3D",
            "lead": "La couverture est vérifiée avec les données réelles du fournisseur avant publication. Aucun succès n’est simulé.",
            "sections": [
                ("Pris en charge", "Des données 3D photoréalistes détaillées existent autour du point confirmé. Vérifiez tout de même le bien exact dans l’aperçu."),
                ("Prise en charge partielle", "La surface 3D existe mais le détail rapproché peut être limité. Une distance caméra plus grande est recommandée."),
                ("Indisponible", "Le détail local est insuffisant. Une notification peut être demandée sans compte."),
                ("Région non prise en charge", "La règle régionale est expliquée séparément d’une adresse sans couverture."),
                ("Erreur technique", "Les erreurs de clé, quota, facturation, réseau ou fournisseur ne constituent pas un résultat négatif pour l’adresse."),
                ("Contrôle visuel", "Une correspondance de couverture ne garantit pas le même détail pour chaque bâtiment. La scène en direct reste le contrôle final."),
            ],
            "faqs": [
                ("Le résultat est-il simulé ?", "Non. Le formulaire appelle le service de production."),
                ("Pourquoi une couverture partielle ?", "Une surface 3D peut exister avec peu de détails de bâtiment."),
                ("Une erreur technique signifie-t-elle indisponible ?", "Non. La requête doit être relancée ou corrigée."),
                ("Analytics conserve-t-il l’adresse ?", "Non. Les adresses et coordonnées brutes sont exclues."),
            ],
            "finalTitle": "Vérifiez l’adresse exacte avant de publier le récit.",
            "cta": "Vérifier une adresse",
            "checkerLabel": "Adresse du bien",
            "checkerPlaceholder": "Rue, ville et pays",
            "checkerButton": "Vérifier la couverture 3D réelle",
            "checkerNote": "Réponse réelle du fournisseur · aucune adresse brute dans Analytics",
        },
        "ru": {
            "title": "Проверка 3D-покрытия по адресу объекта",
            "description": "Проверьте, подходит ли 3D-покрытие адреса для Georivo, и разберитесь в результатах: доступно, частично или недоступно.",
            "category": "3D-покрытие",
            "lead": "Покрытие проверяется по реальным данным провайдера до публикации. Таймера или имитации успешного результата нет.",
            "sections": [
                ("Поддерживается", "Вокруг подтверждённой точки доступны детальные фотореалистичные 3D-данные. Точный объект всё равно нужно проверить в живом превью."),
                ("Частичное покрытие", "3D-поверхность есть, но детализация вблизи может быть ограничена. Рекомендуется увеличить дистанцию камеры."),
                ("Недоступно", "Локальной детализации недостаточно. Можно запросить уведомление без создания аккаунта."),
                ("Неподдерживаемый регион", "Региональное правило объясняется отдельно от отсутствия покрытия по конкретному адресу."),
                ("Техническая ошибка", "Проблемы ключа, квоты, оплаты, сети или провайдера не являются отрицательным ответом по адресу."),
                ("Визуальная проверка", "Наличие покрытия не гарантирует одинаковую детализацию каждого здания. Финальная проверка — живая сцена."),
            ],
            "faqs": [
                ("Ответ имитируется?", "Нет. Форма вызывает production endpoint проверки покрытия."),
                ("Почему покрытие бывает частичным?", "3D-поверхность может быть доступна при ограниченной детализации здания."),
                ("Техническая ошибка означает, что адрес не поддерживается?", "Нет. Запрос нужно повторить или исправить техническую проблему."),
                ("Адрес хранится в аналитике?", "Нет. Сырые адреса и координаты исключены."),
            ],
            "finalTitle": "Проверьте точный адрес до настройки и публикации истории.",
            "cta": "Проверить адрес",
            "checkerLabel": "Адрес объекта",
            "checkerPlaceholder": "Улица, город и страна",
            "checkerButton": "Проверить реальное 3D-покрытие",
            "checkerNote": "Реальный ответ провайдера · сырой адрес не попадает в аналитику",
        },
    },
    "pricing": {
        "en": {
            "title": "Georivo Pricing for Interactive Property Flyovers",
            "description": "Preview supported properties for free, then publish protected 3D location-story links and website embeds with Georivo Solo for €49 per month.",
            "category": "Georivo Solo · €49/month",
            "lead": "Explore and configure a supported property before paying. Subscribe when you are ready to publish protected links and domain-bound website widgets.",
            "sections": [
                ("One clear plan", "Georivo Solo costs €49 per month. It includes up to 10 active widgets and 1,000 visitor-started live 3D plays per calendar month."),
                ("Free property preview", "Address checking, configuration and the local live preview are available before subscription. Payment is required for protected publication, sharing and embedding, not for testing whether a location works."),
                ("What counts as a play", "An ordinary page view does not consume the allowance. A play is counted only when a visitor starts the live 3D scene. Passive poster loading and static explanatory content do not count."),
                ("Publishing controls", "The dashboard stores each configuration and its status. Publishing creates an active protected widget. Revoking pauses public access without deleting the configuration; restoring reactivates it when entitlement and limits permit."),
                ("At the monthly limit", "The hosted page and static explanation remain online, while additional live 3D starts pause until the next allowance period. Georivo does not invent an unannounced overage charge."),
                ("Billing and cancellation", "Stripe processes the recurring subscription and customer portal. Cancellation stops future renewal according to the current billing period. The published Terms and support channel remain authoritative for billing and legal questions."),
            ],
            "faqs": [
                ("Can I preview before subscribing?", "Yes. Check coverage, configure the route and inspect the live preview first."),
                ("How many widgets are included?", "Georivo Solo includes up to 10 active widgets."),
                ("How is usage measured?", "Only visitor-started live 3D sessions count toward the 1,000-play monthly allowance."),
                ("Can I cancel?", "Yes. Subscription management is available through the Stripe customer portal."),
            ],
            "finalTitle": "Preview first. Subscribe when the location story is ready to publish.",
            "cta": "Start Georivo Solo",
        },
        "de": {
            "title": "Georivo Preise für interaktive Immobilienflüge",
            "description": "Unterstützte Immobilien kostenlos prüfen und mit Georivo Solo für 49 € pro Monat geschützte 3D-Links und Website-Widgets veröffentlichen.",
            "category": "Georivo Solo · 49 €/Monat",
            "lead": "Prüfen und konfigurieren Sie eine unterstützte Immobilie vor der Zahlung. Das Abonnement wird erst zur Veröffentlichung benötigt.",
            "sections": [
                ("Ein klarer Tarif", "Georivo Solo kostet 49 € pro Monat und enthält bis zu 10 aktive Widgets sowie 1.000 gestartete Live-3D-Wiedergaben pro Kalendermonat."),
                ("Kostenlose Vorschau", "Adressprüfung, Konfiguration und Live-Vorschau sind vor dem Abonnement möglich."),
                ("Was als Wiedergabe zählt", "Normale Seitenaufrufe zählen nicht. Nur ein vom Besucher gestartetes Live-3D verbraucht das Kontingent."),
                ("Veröffentlichung kontrollieren", "Widgets können veröffentlicht, widerrufen und wiederhergestellt werden, ohne die gespeicherte Konfiguration zu löschen."),
                ("Am Monatslimit", "Die Seite bleibt online, neue Live-3D-Starts pausieren bis zur nächsten Periode. Es gibt keine erfundenen Zusatzgebühren."),
                ("Abrechnung und Kündigung", "Stripe verarbeitet Abonnement und Kundenportal. Die Kündigung stoppt die nächste Verlängerung gemäß Abrechnungsperiode."),
            ],
            "faqs": [
                ("Kann ich vorher testen?", "Ja. Prüfen Sie Abdeckung, Route und Live-Vorschau zuerst."),
                ("Wie viele Widgets?", "Bis zu 10 aktive Widgets."),
                ("Was zählt zum Limit?", "Nur vom Besucher gestartete Live-3D-Sitzungen."),
                ("Kann ich kündigen?", "Ja, über das Stripe-Kundenportal."),
            ],
            "finalTitle": "Zuerst prüfen. Abonnieren, wenn die Geschichte bereit ist.",
            "cta": "Georivo Solo starten",
        },
        "es": {
            "title": "Precio de Georivo para vuelos 3D inmobiliarios",
            "description": "Comprueba propiedades gratis y publica enlaces 3D protegidos y widgets web con Georivo Solo por 49 € al mes.",
            "category": "Georivo Solo · 49 €/mes",
            "lead": "Explora y configura una propiedad compatible antes de pagar. Suscríbete cuando la historia esté lista para publicar.",
            "sections": [
                ("Un plan claro", "Georivo Solo cuesta 49 € al mes e incluye hasta 10 widgets activos y 1.000 inicios de 3D por mes natural."),
                ("Vista previa gratuita", "La comprobación, configuración y vista previa están disponibles antes de suscribirse."),
                ("Qué cuenta como reproducción", "Una visita normal no cuenta. Solo consume el límite cuando el visitante inicia el 3D en vivo."),
                ("Control de publicación", "Publica, revoca y restaura widgets sin borrar la configuración guardada."),
                ("Al llegar al límite", "La página sigue online y se pausan nuevos inicios 3D hasta el siguiente periodo. No hay recargos inventados."),
                ("Facturación y cancelación", "Stripe gestiona la suscripción y el portal. La cancelación detiene la renovación según el periodo vigente."),
            ],
            "faqs": [
                ("¿Puedo probar antes?", "Sí. Comprueba cobertura, ruta y vista previa primero."),
                ("¿Cuántos widgets incluye?", "Hasta 10 widgets activos."),
                ("¿Qué consume el límite?", "Solo sesiones 3D iniciadas por visitantes."),
                ("¿Puedo cancelar?", "Sí, desde el portal de Stripe."),
            ],
            "finalTitle": "Primero revisa. Suscríbete cuando esté listo para publicar.",
            "cta": "Empezar Georivo Solo",
        },
        "fr": {
            "title": "Tarif Georivo pour les survols 3D immobiliers",
            "description": "Prévisualisez gratuitement les biens pris en charge puis publiez des liens 3D protégés et des widgets avec Georivo Solo à 49 € par mois.",
            "category": "Georivo Solo · 49 €/mois",
            "lead": "Explorez et configurez un bien avant de payer. Abonnez-vous lorsque le récit est prêt à être publié.",
            "sections": [
                ("Une offre claire", "Georivo Solo coûte 49 € par mois et comprend jusqu’à 10 widgets actifs et 1 000 démarrages 3D par mois civil."),
                ("Aperçu gratuit", "Vérification, configuration et aperçu sont disponibles avant abonnement."),
                ("Ce qui compte comme lecture", "Une simple page vue ne compte pas. Seul le démarrage du 3D par le visiteur consomme le quota."),
                ("Contrôle de publication", "Publiez, révoquez et restaurez les widgets sans supprimer la configuration."),
                ("À la limite mensuelle", "La page reste en ligne et les nouveaux démarrages sont suspendus. Aucun dépassement non annoncé n’est inventé."),
                ("Facturation et résiliation", "Stripe gère l’abonnement et le portail. La résiliation arrête le renouvellement selon la période en cours."),
            ],
            "faqs": [
                ("Puis-je tester avant ?", "Oui. Vérifiez d’abord la couverture, le parcours et l’aperçu."),
                ("Combien de widgets ?", "Jusqu’à 10 widgets actifs."),
                ("Qu’est-ce qui consomme le quota ?", "Uniquement les sessions 3D démarrées par les visiteurs."),
                ("Puis-je résilier ?", "Oui, depuis le portail Stripe."),
            ],
            "finalTitle": "Prévisualisez d’abord. Abonnez-vous au moment de publier.",
            "cta": "Démarrer Georivo Solo",
        },
        "ru": {
            "title": "Стоимость интерактивных 3D-пролётов Georivo",
            "description": "Бесплатно проверьте объект, затем публикуйте защищённые 3D-ссылки и виджеты с Georivo Solo за €49 в месяц.",
            "category": "Georivo Solo · €49/месяц",
            "lead": "Проверьте и настройте поддерживаемый объект до оплаты. Подписка нужна, когда история готова к публикации.",
            "sections": [
                ("Один понятный тариф", "Georivo Solo стоит €49 в месяц и включает до 10 активных виджетов и 1 000 запусков живого 3D за календарный месяц."),
                ("Бесплатное превью", "Проверка адреса, настройка и живое превью доступны до подписки."),
                ("Что считается запуском", "Обычный просмотр страницы не расходует лимит. Считается только запуск живого 3D посетителем."),
                ("Управление публикацией", "Виджет можно опубликовать, отозвать и восстановить без удаления сохранённой конфигурации."),
                ("При достижении лимита", "Страница остаётся онлайн, новые 3D-запуски приостанавливаются до следующего периода. Скрытых доплат нет."),
                ("Оплата и отмена", "Stripe обрабатывает подписку и клиентский портал. Отмена прекращает следующее продление согласно текущему периоду."),
            ],
            "faqs": [
                ("Можно проверить до подписки?", "Да. Сначала проверьте покрытие, маршрут и живое превью."),
                ("Сколько виджетов включено?", "До 10 активных виджетов."),
                ("Что расходует лимит?", "Только запущенные посетителями живые 3D-сессии."),
                ("Можно отменить подписку?", "Да, через клиентский портал Stripe."),
            ],
            "finalTitle": "Сначала проверьте. Подписывайтесь, когда история готова к публикации.",
            "cta": "Начать с Georivo Solo",
        },
    },
}


RELATED = {
    "how-it-works": [
        ("/coverage", "Check 3D coverage"),
        ("/templates/", "Compare story templates"),
        ("/examples/", "Open live examples"),
    ],
    "coverage": [
        ("/how-it-works", "See how Georivo works"),
        ("/examples/", "Inspect covered examples"),
        ("/pricing", "Review pricing"),
    ],
    "pricing": [
        ("/how-it-works", "See the complete workflow"),
        ("/coverage", "Check an address"),
        ("/embed/", "Understand website embeds"),
    ],
}


def localized_url(path, language):
    if language == "en":
        return path
    return f"/{language}{path}" if path != "/" else f"/{language}"


def render_html(slug, language, page):
    sections = "".join(
        f'<section><span class="money-number">{index:02d}</span><h2>{title}</h2><p>{copy}</p></section>'
        for index, (title, copy) in enumerate(page["sections"], start=1)
    )
    faq = "".join(
        f"<details><summary>{question}</summary><p>{answer}</p></details>"
        for question, answer in page["faqs"]
    )
    related = "".join(
        f'<a href="{localized_url(path, language)}">{label}<span>↗</span></a>'
        for path, label in RELATED[slug]
    )
    return (
        f'<p class="money-lead">{page["lead"]}</p>'
        f'<div class="money-grid">{sections}</div>'
        f'<section class="money-faq"><h2>FAQ</h2>{faq}</section>'
        f'<nav class="money-related" aria-label="Related pages">{related}</nav>'
    )


def page_record(slug, now):
    job_id = hashlib.sha256(f"georivo:/{slug}".encode()).hexdigest()[:24]
    english = PAGES[slug]["en"]
    cta_url = "/dashboard?startCheckout=1" if slug == "pricing" else "/#create"
    translations = {}
    for language in LANGUAGES[1:]:
        page = PAGES[slug][language]
        translations[language] = {
            "title": page["title"],
            "description": page["description"],
            "category": page["category"],
            "draftHtml": render_html(slug, language, page),
            "primaryCta": {"label": page["cta"], "url": cta_url},
            "finalTitle": page["finalTitle"],
            **{
                key: page[key]
                for key in ("checkerLabel", "checkerPlaceholder", "checkerButton", "checkerNote")
                if key in page
            },
        }
    return {
        "id": job_id,
        "slug": slug,
        "contentType": "money_page",
        "pageType": "seo_money_page",
        "targetPath": f"/{slug}",
        "language": "en",
        "languages": list(LANGUAGES),
        "translations": translations,
        "title": english["title"],
        "description": english["description"],
        "category": english["category"],
        "heroImage": HEROES[slug],
        "draftHtml": render_html(slug, "en", english),
        "primaryCta": {"label": english["cta"], "url": cta_url},
        "finalEyebrow": "Georivo Location Story Widget",
        "finalTitle": english["finalTitle"],
        "checkerLabel": english.get("checkerLabel"),
        "checkerPlaceholder": english.get("checkerPlaceholder"),
        "checkerButton": english.get("checkerButton"),
        "checkerNote": english.get("checkerNote"),
        "editorial": {
            "author": "Georivo Editorial",
            "reviewer": "Georivo Product Review",
            "owner": "Georivo Content",
            "factCheckedAt": now[:10],
            "reviewDueAt": "2026-10-25",
            "reviewCadence": "every 90 days or after a material product, pricing, coverage, or provider change",
            "sources": [
                {
                    "title": "Georivo product",
                    "publisher": "Georivo",
                    "publicUrl": "https://georivo.com/",
                    "accessedAt": now[:10],
                }
            ],
        },
        "publishedAt": PUBLISHED_AT,
        "updatedAt": now,
    }


def publish(db_path, native_root):
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    site = conn.execute("select domain from sites where id=?", (SITE_ID,)).fetchone()
    if not site or site["domain"] != "georivo.com":
        raise SystemExit("Blog Core site 14 is not georivo.com")
    published_root = native_root / "published"
    published_root.mkdir(parents=True, exist_ok=True)
    changed = []
    for slug in PAGES:
        record = page_record(slug, now)
        job_id = record["id"]
        sources = {
            "contentType": "money_page",
            "pageType": "seo_money_page",
            "targetPath": record["targetPath"],
            "canonicalGroup": f"georivo:money_page:{slug}",
            "language": "en",
            "languages": list(LANGUAGES),
            "editorial": record["editorial"],
            "primaryCta": record["primaryCta"],
            "managedBy": "Blog Core native content store",
        }
        existing = conn.execute("select created_at from content_jobs where id=?", (job_id,)).fetchone()
        created_at = existing["created_at"] if existing else now
        conn.execute(
            """
            insert into content_jobs(
              id,site_id,topic,slug,status,title,description,category,hero_image,draft_html,
              faq_json,error,sources_json,visibility,published_url,created_at,updated_at
            ) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            on conflict(id) do update set
              status=excluded.status,title=excluded.title,description=excluded.description,
              category=excluded.category,hero_image=excluded.hero_image,draft_html=excluded.draft_html,
              faq_json=excluded.faq_json,error=null,sources_json=excluded.sources_json,
              visibility=excluded.visibility,published_url=excluded.published_url,updated_at=excluded.updated_at
            """,
            (
                job_id, SITE_ID, record["title"], slug, "PUBLISHED", record["title"],
                record["description"], "SEO Money Page", record["heroImage"], record["draftHtml"],
                json.dumps(PAGES[slug]["en"]["faqs"], ensure_ascii=False), None,
                json.dumps(sources, ensure_ascii=False, separators=(",", ":")), "public",
                f"https://georivo.com/{slug}", created_at, now,
            ),
        )
        for language in LANGUAGES[1:]:
            localized = record["translations"][language]
            conn.execute(
                """
                insert into content_job_localizations(
                  site_id,job_id,language,slug,title,description,category,draft_html,faq_json,created_at,updated_at
                ) values(?,?,?,?,?,?,?,?,?,?,?)
                on conflict(job_id,language) do update set
                  slug=excluded.slug,title=excluded.title,description=excluded.description,
                  category=excluded.category,draft_html=excluded.draft_html,
                  faq_json=excluded.faq_json,updated_at=excluded.updated_at
                """,
                (
                    SITE_ID, job_id, language, slug, localized["title"], localized["description"],
                    localized["category"], localized["draftHtml"],
                    json.dumps(PAGES[slug][language]["faqs"], ensure_ascii=False), created_at, now,
                ),
            )
        conn.execute(
            "insert into content_job_logs(site_id,job_id,ts,level,step,message) values(?,?,?,?,?,?)",
            (SITE_ID, job_id, now, "INFO", "money-page-publish", f"Published Blog Core money page /{slug}"),
        )
        path = published_root / f"money--{slug}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed.append({"slug": slug, "id": job_id, "path": str(path)})
    conn.commit()
    conn.close()
    print(json.dumps({"published": changed}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="/var/www/blog.yas.ooo/data/blog_core.sqlite3")
    parser.add_argument("--native-root", default="/var/www/georivo-blog/data/blog-core")
    args = parser.parse_args()
    publish(Path(args.db), Path(args.native_root))
