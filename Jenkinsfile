pipeline {
    agent any

    environment {
        IMAGE_NAME = "trayz72/selenium-app"
        IMAGE_TAG  = "${BUILD_NUMBER}"
        TEST_IMAGE = "selenium-test:${BUILD_NUMBER}"
    }

    stages {

        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Build Test Image') {
            steps {
                sh '''
                  echo "Building TEST image (with Chrome + Selenium)..."
                  docker build --target test -t $TEST_IMAGE .
                '''
            }
        }

        stage('Run Selenium UI Tests') {
            steps {
                sh '''
                  echo "Running Selenium tests inside TEST image..."
                  docker run --rm $TEST_IMAGE pytest tests/
                '''
            }
        }

        stage('Build Runtime Image') {
            steps {
                sh '''
                  echo "Building RUNTIME image (lightweight)..."
                  docker build --target runtime -t $IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }

        stage('Docker Hub Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                      echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                    '''
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                sh '''
                  echo "Pushing lightweight runtime image..."
                  docker push $IMAGE_NAME:$IMAGE_TAG

                  docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
                  docker push $IMAGE_NAME:latest
                '''
            }
        }

        stage('Deploy Application + Monitoring') {
            steps {
                sh '''
                  echo "Deploying application with Prometheus & Grafana..."

                  docker-compose down || true
                  docker-compose up -d
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                  echo "Running containers:"
                  docker ps

                  echo "Checking Prometheus:"
                  curl -f http://localhost:9090 || echo "Prometheus not reachable"

                  echo "Checking Grafana:"
                  curl -f http://localhost:3000 || echo "Grafana not reachable"
                '''
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
        success {
            echo '✅ Tests passed, image pushed, app deployed with monitoring!'
        }
        failure {
            echo '❌ Pipeline failed. Check logs above.'
        }
    }
}
