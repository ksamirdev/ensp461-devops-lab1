import hudson.model.*
import hudson.plugins.git.*
import hudson.security.*
import jenkins.model.*
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def j = Jenkins.get()
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('samir', new File('/var/lib/jenkins/.admin-password').text.trim()).setFullName('Samir Kumar Gupta')
j.setSecurityRealm(realm)
def auth = new FullControlOnceLoggedInAuthorizationStrategy()
auth.setAllowAnonymousRead(false)
j.setAuthorizationStrategy(auth)
if (j.getItem('text-stats-pipeline') == null) {
    def scm = new GitSCM(GitSCM.createRepoList('https://github.com/ksamirdev/ensp461-devops-lab1.git', null),
        [new BranchSpec('*/main')], null, null, [])
    def job = j.createProject(WorkflowJob, 'text-stats-pipeline')
    job.setDescription('ENSP461 Lab 1 - build, test, package and deploy the text statistics service')
    job.setDefinition(new CpsScmFlowDefinition(scm, 'Jenkinsfile'))
    job.save()
}
j.save()
