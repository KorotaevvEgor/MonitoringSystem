#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
СИСТЕМА МОНИТОРИНГА НА ОСНОВЕ PROMETHEUS, GRAFANA И BLACKBOX EXPORTER
======================================================================

Описание:
    Этот модуль содержит вспомогательные утилиты для управления
    системой мониторинга, развернутой с помощью Docker Compose.
    
    Система включает в себя:
    - Prometheus: сбор и хранение метрик
    - Grafana: визуализация метрик и создание дашбордов
    - Node Exporter: экспорт системных метрик хоста
    - Blackbox Exporter: проверка доступности внешних ресурсов

Автор: Система мониторинга
Версия: 1.0
Дата: 2024
"""

import os
import sys
import time
import subprocess
import json
import requests
from typing import Dict, List, Optional
from pathlib import Path


class MonitoringSystemManager:
    """
    Класс для управления системой мониторинга
    
    Предоставляет методы для:
    - Запуска и остановки системы мониторинга
    - Проверки статуса сервисов
    - Получения метрик из Prometheus
    - Управления конфигурациями
    """
    
    def __init__(self, project_dir: str = None):
        """
        Инициализация менеджера системы мониторинга
        
        Args:
            project_dir (str): Путь к директории проекта с docker-compose.yml
        """
        # Определяем корневую директорию проекта
        self.project_dir = Path(project_dir) if project_dir else Path(__file__).parent
        
        # Пути к важным файлам конфигурации
        self.docker_compose_file = self.project_dir / "docker-compose.yml"
        self.prometheus_config = self.project_dir / "prometheus" / "prometheus.yml"
        self.blackbox_config = self.project_dir / "blackbox" / "blackbox.yml"
        
        # URLs сервисов мониторинга (по умолчанию для локального развертывания)
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3000"
        self.blackbox_url = "http://localhost:9115"
        self.node_exporter_url = "http://localhost:9100"
        
        # Проверяем наличие необходимых файлов
        self._validate_project_structure()
    
    def _validate_project_structure(self) -> None:
        """
        Проверяет наличие необходимых файлов конфигурации
        
        Raises:
            FileNotFoundError: Если отсутствуют критически важные файлы
        """
        required_files = [
            self.docker_compose_file,
            self.prometheus_config,
            self.blackbox_config
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Отсутствует необходимый файл конфигурации: {file_path}"
                )
        
        print("✅ Структура проекта корректна")
    
    def start_monitoring(self) -> bool:
        """
        Запускает систему мониторинга с помощью Docker Compose
        
        Returns:
            bool: True если система успешно запущена, False в противном случае
        """
        try:
            print("🚀 Запуск системы мониторинга...")
            
            # Переходим в директорию проекта для корректной работы docker-compose
            original_dir = os.getcwd()
            os.chdir(self.project_dir)
            
            # Запускаем docker-compose в фоновом режиме
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Возвращаемся в исходную директорию
            os.chdir(original_dir)
            
            print("✅ Система мониторинга запущена")
            print("\n📊 Доступные интерфейсы:")
            print(f"   • Prometheus: {self.prometheus_url}")
            print(f"   • Grafana: {self.grafana_url} (admin/admin)")
            print(f"   • Node Exporter: {self.node_exporter_url}")
            print(f"   • Blackbox Exporter: {self.blackbox_url}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при запуске системы мониторинга: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {str(e)}")
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Останавливает систему мониторинга
        
        Returns:
            bool: True если система успешно остановлена, False в противном случае
        """
        try:
            print("🛑 Остановка системы мониторинга...")
            
            # Переходим в директорию проекта
            original_dir = os.getcwd()
            os.chdir(self.project_dir)
            
            # Останавливаем и удаляем контейнеры
            result = subprocess.run(
                ["docker-compose", "down"],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Возвращаемся в исходную директорию
            os.chdir(original_dir)
            
            print("✅ Система мониторинга остановлена")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при остановке системы: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {str(e)}")
            return False
    
    def check_services_health(self) -> Dict[str, bool]:
        """
        Проверяет доступность всех сервисов мониторинга
        
        Returns:
            Dict[str, bool]: Словарь с результатами проверки каждого сервиса
        """
        services = {
            "Prometheus": self.prometheus_url,
            "Grafana": self.grafana_url,
            "Node Exporter": self.node_exporter_url,
            "Blackbox Exporter": self.blackbox_url
        }
        
        results = {}
        
        print("🔍 Проверка доступности сервисов...")
        
        for service_name, url in services.items():
            try:
                # Отправляем HTTP запрос с таймаутом
                response = requests.get(url, timeout=5)
                is_healthy = response.status_code == 200
                
                status_icon = "✅" if is_healthy else "❌"
                print(f"   {status_icon} {service_name}: {'Доступен' if is_healthy else 'Недоступен'}")
                
                results[service_name] = is_healthy
                
            except requests.exceptions.RequestException:
                print(f"   ❌ {service_name}: Недоступен (таймаут или ошибка соединения)")
                results[service_name] = False
        
        return results
    
    def get_prometheus_metrics(self, query: str) -> Optional[Dict]:
        """
        Выполняет запрос к Prometheus API для получения метрик
        
        Args:
            query (str): PromQL запрос для получения метрик
        
        Returns:
            Optional[Dict]: Результат запроса или None в случае ошибки
        """
        try:
            # Формируем URL для API запроса
            api_url = f"{self.prometheus_url}/api/v1/query"
            params = {"query": query}
            
            # Отправляем запрос к Prometheus API
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при запросе метрик из Prometheus: {str(e)}")
            return None
    
    def show_system_info(self) -> None:
        """
        Отображает информацию о системе мониторинга
        """
        print("\n" + "="*60)
        print("📊 СИСТЕМА МОНИТОРИНГА - ИНФОРМАЦИЯ")
        print("="*60)
        
        print(f"📁 Директория проекта: {self.project_dir}")
        print(f"🐳 Docker Compose файл: {self.docker_compose_file}")
        print(f"⚙️  Конфигурация Prometheus: {self.prometheus_config}")
        print(f"⚙️  Конфигурация Blackbox: {self.blackbox_config}")
        
        print("\n🌐 URL сервисов:")
        print(f"   • Prometheus (метрики): {self.prometheus_url}")
        print(f"   • Grafana (дашборды): {self.grafana_url}")
        print(f"   • Node Exporter (системные метрики): {self.node_exporter_url}")
        print(f"   • Blackbox Exporter (внешние проверки): {self.blackbox_url}")
        
        print("\n🔧 Возможности системы:")
        print("   • Мониторинг системных ресурсов (CPU, RAM, диск, сеть)")
        print("   • Проверка доступности внешних HTTP/HTTPS ресурсов")
        print("   • Визуализация метрик в Grafana")
        print("   • Настраиваемые алерты и уведомления")
        
        print("\n⚠️  ПРИМЕЧАНИЕ ПО БЕЗОПАСНОСТИ:")
        print("   В данной конфигурации НЕТ аутентификации для сервисов!")
        print("   Для production использования необходимо:")
        print("   • Настроить аутентификацию в Grafana")
        print("   • Настроить Basic Auth для Prometheus")
        print("   • Использовать HTTPS соединения")
        print("   • Ограничить доступ к портам через firewall")


def main():
    """
    Основная функция для демонстрации работы системы мониторинга
    
    Позволяет пользователю интерактивно управлять системой мониторинга
    через простое консольное меню.
    """
    # Создаем экземпляр менеджера системы мониторинга
    manager = MonitoringSystemManager()
    
    while True:
        print("\n" + "="*50)
        print("🖥️  СИСТЕМА МОНИТОРИНГА - УПРАВЛЕНИЕ")
        print("="*50)
        print("1. 🚀 Запустить систему мониторинга")
        print("2. 🛑 Остановить систему мониторинга")
        print("3. 🔍 Проверить статус сервисов")
        print("4. 📊 Показать информацию о системе")
        print("5. 📈 Получить пример метрик из Prometheus")
        print("6. 🚪 Выход")
        
        choice = input("\n👉 Выберите действие (1-6): ").strip()
        
        if choice == "1":
            # Запуск системы мониторинга
            success = manager.start_monitoring()
            if success:
                print("\n⏳ Ожидание инициализации сервисов (30 секунд)...")
                time.sleep(30)  # Даем время сервисам полностью запуститься
                manager.check_services_health()
        
        elif choice == "2":
            # Остановка системы мониторинга
            manager.stop_monitoring()
        
        elif choice == "3":
            # Проверка статуса всех сервисов
            health_results = manager.check_services_health()
            
            healthy_count = sum(health_results.values())
            total_count = len(health_results)
            
            print(f"\n📊 Общий статус: {healthy_count}/{total_count} сервисов доступны")
        
        elif choice == "4":
            # Показать информацию о системе
            manager.show_system_info()
        
        elif choice == "5":
            # Получить пример метрик из Prometheus
            print("\n📈 Получение примера метрик из Prometheus...")
            
            # Пример PromQL запросов
            example_queries = [
                ("up", "Статус доступности всех целей"),
                ("node_load1", "Загрузка системы за 1 минуту"),
                ("probe_success", "Результаты внешних проверок")
            ]
            
            for query, description in example_queries:
                print(f"\n🔍 {description} ({query}):")
                result = manager.get_prometheus_metrics(query)
                
                if result and result.get("status") == "success":
                    data = result.get("data", {}).get("result", [])
                    if data:
                        for item in data[:3]:  # Показываем только первые 3 результата
                            metric = item.get("metric", {})
                            value = item.get("value", [])
                            if len(value) >= 2:
                                print(f"   • {metric}: {value[1]}")
                    else:
                        print("   (нет данных)")
                else:
                    print("   ❌ Ошибка получения данных")
        
        elif choice == "6":
            # Выход из программы
            print("\n👋 До свидания!")
            break
        
        else:
            print("\n❌ Некорректный выбор. Пожалуйста, выберите число от 1 до 6.")
        
        # Пауза перед показом меню снова
        input("\n⏸️  Нажмите Enter для продолжения...")


if __name__ == "__main__":
    """
    Точка входа в программу
    
    При запуске этого файла напрямую будет запущено интерактивное меню
    для управления системой мониторинга.
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Программа прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {str(e)}")
        sys.exit(1)
