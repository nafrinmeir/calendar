pipeline {
    agent any

    environment {
        RELEASE_NAME = "my-calendar"
        CHART_DIR = "./calendar-chart"
        // הגדרה ישירה של הנתיב ל-Helm
        HELM_CMD = "C:\\Helm\\helm.exe"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                echo "✅ Code checked out from GitHub successfully!"
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    echo "🛠️ Building Calendar API Image..."
                    bat 'docker build -t calendar-api:latest ./calendar_api'

                    echo "🛠️ Building Calendar Frontend Image..."
                    bat 'docker build -t calendar-front:latest ./calendar_front'

                    echo "🛠️ Building Dashboard Image..."
                    bat 'docker build -t dashboard:latest ./dashboard'
                }
            }
        }

        stage('Deploy to K8s (Helm)') {
            steps {
                script {
                    echo "🚀 Deploying with Helm using absolute path..."
                    // שימוש במשתנה הסביבה שמצביע לנתיב המלא
                    bat "\"${HELM_CMD}\" upgrade --install ${RELEASE_NAME} ${CHART_DIR}"
                }
            }
        }

        stage('Apply Updates (Rollout)') {
            steps {
                script {
                    echo "🔄 Restarting pods to pull the new images..."
                    bat 'kubectl rollout restart deployment calendar-api'
                    bat 'kubectl rollout restart deployment calendar-front'
                    bat 'kubectl rollout restart deployment dashboard'
                }
            }
        }
    }

    post {
        success {
            echo "🎉 SUCCESS! The Calendar App was automatically built and deployed to Kubernetes."
        }
        failure {
            echo "❌ FAILED! Something went wrong in the pipeline. Check the logs above."
        }
    }
}
