# ups_monitor
Сбор метрик pwrstat

scrape_configs:
  - job_name: 'ups'
    static_configs:
      - targets: ['localhost:8000']