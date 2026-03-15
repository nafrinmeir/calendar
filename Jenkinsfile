pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "nafrin" 
        RELEASE_NAME = "my-calendar"
        CHART_DIR = "./calendar-chart"
        KUBECONFIG = "C:\\Users\\MyPc\\.kube\\config"
        HELM_CMD = "C:\\Helm\\helm.exe"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                echo "✅ Code checked out from GitHub successfully!"
            }
        }

        stage('Build Local Images') {
            steps {
                script {
                    echo "🛠️ Building Images locally..."
                    bat 'docker build -t calendar-api:latest ./calendar_api'
                    bat 'docker build -t calendar-front:latest ./calendar_front'
                    bat 'docker build -t dashboard:latest ./dashboard'
                }
            }
        }

        stage('Test All Built Images (Pre-Push)') {
            steps {
                script {
                    echo "🚀 Starting temporary containers for ALL services..."
                    // מרימים את כולם במקביל על פורטים זמניים שלא מתנגשים עם כלום
                    bat 'docker run -d --name temp-api -p 5091:5001 calendar-api:latest'
                    bat 'docker run -d --name temp-front -p 5092:5002 calendar-front:latest'
                    bat 'docker run -d --name temp-dash -p 5090:5000 dashboard:latest'
                    
                    try {
                        echo "🧪 Running Tests against all temporary containers..."
                        // מריצים את פקודת הטסטים מול שלושתם
                        bat '''
                        docker run --rm -v "%WORKSPACE%:/app" -w /app python:3.9-slim sh -c "pip install pytest requests && pytest test_services.py -v -s"
                        '''
                        echo "✅ All 3 tests passed! The images are totally solid."
                    } finally {
                        echo "🧹 Cleaning up temporary containers..."
                        // גם אם טסט נכשל, אנחנו מוחקים את כל ה-3 כדי לא להשאיר זבל בשרת
                        bat 'docker rm -f temp-api temp-front temp-dash'
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo "🔒 Logging into Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: 'docker_hub_user', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                        bat 'docker login -u %DOCKER_USER% -p %DOCKER_PASS%'
                        
                        echo "🏷️ Tagging images..."
                        bat "docker tag calendar-api:latest ${DOCKERHUB_USER}/calendar-api:latest"
                        bat "docker tag calendar-front:latest ${DOCKERHUB_USER}/calendar-front:latest"
                        bat "docker tag dashboard:latest ${DOCKERHUB_USER}/dashboard:latest"

                        echo "☁️ Pushing images to Docker Hub..."
                        bat "docker push ${DOCKERHUB_USER}/calendar-api:latest"
                        bat "docker push ${DOCKERHUB_USER}/calendar-front:latest"
                        bat "docker push ${DOCKERHUB_USER}/dashboard:latest"
                    }
                }
            }
        }

        stage('Deploy to K8s (Helm)') {
            steps {
                script {
                    echo "🚀 Deploying with Helm..."
                    bat "\"${HELM_CMD}\" upgrade --install ${RELEASE_NAME} ${CHART_DIR}"
                }
            }
        }

        stage('Apply Updates (Rollout)') {
            steps {
                script {
                    echo "🔄 Restarting pods to pull the NEW images from Docker Hub..."
                    withEnv(["KUBECONFIG=${env.KUBECONFIG}"]) {
                        bat 'kubectl rollout restart deployment calendar-api'
                        bat 'kubectl rollout restart deployment calendar-front'
                        bat 'kubectl rollout restart deployment dashboard'
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🎉 SUCCESS! All images built, fully tested locally, pushed to Docker Hub, and deployed!"
        }
        failure {
            echo "❌ FAILED! Pipeline stopped. If tests failed, nothing was pushed and K8s is safe."
        }
    }
}
