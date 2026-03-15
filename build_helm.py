import os

helm_structure = {
    "calendar-chart/Chart.yaml": """apiVersion: v2
name: calendar-app
description: A Production-ready Helm chart with LoadBalancers
type: application
version: 0.1.0
appVersion: "1.0.0"
""",

    "calendar-chart/values.yaml": """# הגדרות מרכזיות לכל המערכת

appVersion: "latest"

mongodb:
  image: mongo:latest
  port: 27017
  # שם מסד נתונים נפרד לחלוטין עבור K8s
  dbName: calendar_k8s_db

api:
  image: calendar-api:latest
  pullPolicy: Never
  targetPort: 5001
  servicePort: 5011
  replicas: 1

front:
  image: calendar-front:latest
  pullPolicy: Never
  targetPort: 5002
  servicePort: 5012
  replicas: 1

dashboard:
  image: dashboard:latest
  pullPolicy: Never
  targetPort: 5000
  servicePort: 5010
  replicas: 1
""",

    "calendar-chart/templates/mongodb.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
spec:
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: {{ .Values.mongodb.image }}
        ports:
        - containerPort: {{ .Values.mongodb.port }}
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  selector:
    app: mongodb
  ports:
  - port: {{ .Values.mongodb.port }}
    targetPort: {{ .Values.mongodb.port }}
""",

    "calendar-chart/templates/api.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: calendar-api
spec:
  replicas: {{ .Values.api.replicas }}
  selector:
    matchLabels:
      app: calendar-api
  template:
    metadata:
      labels:
        app: calendar-api
    spec:
      containers:
      - name: calendar-api
        image: {{ .Values.api.image }}
        imagePullPolicy: {{ .Values.api.pullPolicy }}
        env:
        - name: MONGO_URI
          # חיבור ישיר ל-DB הנפרד שיצרנו
          value: "mongodb://mongodb:{{ .Values.mongodb.port }}/{{ .Values.mongodb.dbName }}"
        ports:
        - containerPort: {{ .Values.api.targetPort }}
---
apiVersion: v1
kind: Service
metadata:
  name: calendar-api
spec:
  type: LoadBalancer # זה מה שחוסך את ה-Port Forward!
  selector:
    app: calendar-api
  ports:
  - port: {{ .Values.api.servicePort }}
    targetPort: {{ .Values.api.targetPort }}
""",

    "calendar-chart/templates/front.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: calendar-front
spec:
  replicas: {{ .Values.front.replicas }}
  selector:
    matchLabels:
      app: calendar-front
  template:
    metadata:
      labels:
        app: calendar-front
    spec:
      containers:
      - name: calendar-front
        image: {{ .Values.front.image }}
        imagePullPolicy: {{ .Values.front.pullPolicy }}
        env:
        - name: API_URL
          value: "http://localhost:{{ .Values.api.servicePort }}"
        - name: APP_VERSION
          value: "{{ .Values.appVersion }}"
        ports:
        - containerPort: {{ .Values.front.targetPort }}
---
apiVersion: v1
kind: Service
metadata:
  name: calendar-front
spec:
  type: LoadBalancer # חשוף החוצה
  selector:
    app: calendar-front
  ports:
  - port: {{ .Values.front.servicePort }}
    targetPort: {{ .Values.front.targetPort }}
""",

    "calendar-chart/templates/dashboard.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: dashboard
spec:
  replicas: {{ .Values.dashboard.replicas }}
  selector:
    matchLabels:
      app: dashboard
  template:
    metadata:
      labels:
        app: dashboard
    spec:
      containers:
      - name: dashboard
        image: {{ .Values.dashboard.image }}
        imagePullPolicy: {{ .Values.dashboard.pullPolicy }}
        env:
        - name: FRONT_URL
          value: "http://calendar-front:{{ .Values.front.servicePort }}/health"
        - name: API_URL
          value: "http://calendar-api:{{ .Values.api.servicePort }}/health"
        - name: EXT_FRONT_URL
          value: "http://localhost:{{ .Values.front.servicePort }}"
        - name: EXT_API_URL
          value: "http://localhost:{{ .Values.api.servicePort }}"
        - name: APP_VERSION
          value: "{{ .Values.appVersion }}"
        ports:
        - containerPort: {{ .Values.dashboard.targetPort }}
---
apiVersion: v1
kind: Service
metadata:
  name: dashboard
spec:
  type: LoadBalancer # חשוף החוצה
  selector:
    app: dashboard
  ports:
  - port: {{ .Values.dashboard.servicePort }}
    targetPort: {{ .Values.dashboard.targetPort }}
"""
}

base_dir = "."
for file_path, content in helm_structure.items():
    full_path = os.path.join(base_dir, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Helm Chart updated with LoadBalancers and external links!")
