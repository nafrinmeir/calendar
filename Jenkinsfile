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

        stage('Test Built Image (Pre-Push)') {
            steps {
                script {
                    echo "🚀 Starting a temporary container from the newly built image..."
                    // מריץ את האימג' ברקע על פורט 5099 כדי לא להתנגש עם דברים אחרים
                    bat 'docker run -d --name temp-api-test -p 5099:5001 calendar-api:latest'
                    
                    try {
                        echo "🧪 Running Tests against the temporary container..."
                        // מריץ את קובץ הבדיקה מול הקונטיינר הזמני
                        bat '''
                        docker run --rm -e TEST_URL="http://host.docker.internal:5099/health" -v "%WORKSPACE%:/app" -w /app python:3.9-slim sh -c "pip install pytest requests && pytest test_api_live.py -v -s"
                        '''
                        echo "✅ Tests passed! The image is solid and ready to be pushed."
                    } finally {
                        echo "🧹 Cleaning up temporary container..."
                        // בלוק זה ירוץ תמיד וימחק את הקונטיינר הזמני, כדי שלא נשאיר "לכלוך" בשרת
                        bat 'docker rm -f temp-api-test'
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
            echo "🎉 SUCCESS! Image built, tested locally, pushed to Docker Hub, and deployed to K8s!"
        }
        failure {
            echo "❌ FAILED! The pipeline stopped. Check the logs. If the test failed, NOTHING was pushed to Docker Hub."
        }
    }
}
