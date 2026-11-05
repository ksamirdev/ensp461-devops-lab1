set -u
. /lab/tools/rec.sh /lab/evidence/logs/q6-jenkins-setup.log
rec "sudo mkdir -p /etc/systemd/system/jenkins.service.d"
rec "printf '[Service]\nEnvironment=\"JAVA_OPTS=-Djava.awt.headless=true -Djenkins.install.runSetupWizard=false\"\n' | sudo tee /etc/systemd/system/jenkins.service.d/override.conf"
V=$(curl -fsSL https://api.github.com/repos/jenkinsci/plugin-installation-manager-tool/releases/latest | grep -oE '"tag_name": *"[^"]+"' | cut -d'"' -f4)
rec "curl -fsSL -o /tmp/jpm.jar https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/$V/jenkins-plugin-manager-$V.jar"
rec "sudo -u jenkins java -jar /tmp/jpm.jar --war /usr/share/java/jenkins.war -d /var/lib/jenkins/plugins --plugins workflow-aggregator git junit pipeline-stage-view pipeline-graph-view 2>&1 | tail -3"
sudo sh -c 'openssl rand -hex 16 > /var/lib/jenkins/.admin-password; chown jenkins /var/lib/jenkins/.admin-password; chmod 600 /var/lib/jenkins/.admin-password; mkdir -p /var/lib/jenkins/init.groovy.d; cp /lab/tools/jenkins-init.groovy /var/lib/jenkins/init.groovy.d/; chown -R jenkins /var/lib/jenkins/init.groovy.d'
rec "sudo systemctl daemon-reload && sudo systemctl restart jenkins && systemctl is-active jenkins"
rec "sudo install -m 755 ~/ensp461-devops-lab1/deploy/text-stats-deploy /usr/local/bin/text-stats-deploy"
rec "sudo install -m 644 ~/ensp461-devops-lab1/deploy/text-stats.service /etc/systemd/system/text-stats.service"
rec "echo 'jenkins ALL=(root) NOPASSWD: /usr/local/bin/text-stats-deploy' | sudo tee /etc/sudoers.d/jenkins-deploy"
rec "sudo chmod 440 /etc/sudoers.d/jenkins-deploy && sudo visudo -c -f /etc/sudoers.d/jenkins-deploy"
rec "sudo mkdir -p /opt/text-stats && sudo systemctl daemon-reload && sudo systemctl enable text-stats"
