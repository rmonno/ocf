import uuid
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.views.generic import simple
from vt_manager.controller.drivers.VTDriver import VTDriver
from pypelib.RuleTable import RuleTable
from vt_manager.controller.policies.RuleTableManager import RuleTableManager
from pypelib.Rule import Rule 

@login_required
def rule_table_view(request, TableName = None):
	
	if (not request.user.is_superuser):

               return simple.direct_to_template(request,
                                                 template = 'not_admin.html',
                                                 extra_context = {'user':request.user},
                                                )

        else: #Admin
        	ruleTable = RuleTableManager.getInstance(RuleTableManager.getDefaultName())

        	return simple.direct_to_template(request,
                	                         template = 'policyEngine/table_view.html',
                        	                 extra_context = {'user': request.user,
                                                                  'table':ruleTable},
                                	        )

def policy_create(request,table):

	errors = []
        rules = []
	mapps = RuleTableManager.getActionMappings()
	priorityList = RuleTableManager.getPriorityList()

	return simple.direct_to_template(request,
                                          template = 'policyEngine/policy_create.html',
                                          extra_context = {'user': request.user,
                                                           'CurrentTable': table,
							   'mappings':mapps,
							   'priorityList':priorityList,
							   'allMappings':RuleTableManager.GetResolverMappings(table),
							   'ConditionMappings':RuleTableManager.getConditionMappings(),
                                                           'ActionMappings':RuleTableManager.getActionMappings()},
                                        )

def rule_create(request,table_name=None):

	errors = list()
	formMode = request.POST.get("conditionMode")
	tableName = request.POST.get("table")
	PreviousPriority = request.POST.get("ppriority")
        editing = request.POST.get("editing")
        ruleid = request.POST.get("uuid")
        ruleCondition = request.POST.get("condition")
        ruleDesc = request.POST.get("description")
        ruleError = request.POST.get("error_message")
        ruleType = request.POST.get("type")
        ruleAction = request.POST.get("action")
        ruleValue = request.POST.get("value")
        rulePriority = request.POST.get("priority")
        ruleEnable = request.POST.get("enable")
        previousTable = request.POST.get("hidden_name")
	expertRule = request.POST.get("expertRule")
	newConditions = request.POST.get("conditionID")	
	saved = request.POST.get("saved")

        if rulePriority == 'Last' or rulePriority == '':
                priority = None
        else:
                priority = int(rulePriority)
	#Avoid empty fields
        if ruleDesc == "":
                errors.append("Description Field is empty")
        if ruleError == "":
                errors.append("Error Message field is empty")
        if ruleCondition == "":
                errors.append("Condition field is empty")
        if request.POST.get("enable") == 'enable':
           enable = True
        else:
           enable = False
	if ruleType == "terminal":
		ruleType = ""
	#Rule String convertion required
	if formMode == "easy":
        	strings = "if " + ruleCondition +  " then " + ruleValue + " " + ruleType  + " do " + ruleAction + " denyMessage " + ruleError + " #" + ruleDesc
	else:
		strings = expertRule
	
	try:
		if errors:
                        raise Exception("")	
		print "EDITING:",editing
		if editing == '1':
                	print 'editing...'
			#Editing Rules Case:
                	if previousTable == tableName:
				try:

					RuleTableManager.editRule(strings,enable,priority,PreviousPriority,tableName)
				except Exception as e:
					raise e
                	else:
				#Moving a rule to a different RuleTable --> this is not possible yet 
                        	print 'Changing table...'
                        	RuleTableManager.AddRule(strings,enable,priority,tableName=tableName)
                        	print 'successful add to ' + tableName
                        	RuleTableManager.RemoveRule(None,int(PreviousPriority),'oldTableName')
                        	print 'remove from ' +  previousTable + ' successful'
        	else:
                	RuleTableManager.AddRule(strings,enable,priority,tableName=tableName)

                return HttpResponseRedirect("/policies")		

	except Exception as e:

		errors.append(e)
		errors.insert(0,"The Rule cannot be generated. Reason(s):")#Insterting the main message error in the first position of the table
		priority = RuleTableManager.getPriorityList(tableName)
		actionList = RuleTableManager.SetActionList(ruleAction,RuleTableManager.getActionMappings())
		priority = RuleTableManager.getPriorityList(tableName)
		
		#if a rule index is the last, insert "LAST" in the rule priority instead the true index.
		try:
			int(rulePriority)
			if int(rulePriority) in priority:
				priority.pop(priority.index(int(rulePriority)))
		except:
			rulePriority = "Last"

		if ruleValue == "accept":
			value2 = ["deny"]
		else:
			value2 = ["accept"]

		if ruleType == "nonterminal":
			type2 = ["terminal"]
		else:
			ruleType = "terminal"
			type2 = ["nonterminal"]

		if saved == "True" or ruleid == "":

			return simple.direct_to_template(request,
        	        	template = 'policyEngine/policy_create.html',
                		extra_context = {'user': request.user,
						 'saved':True,
						 'CurrentTable':tableName,
                                        	 'priority':priority,
	                                         'enabled':ruleEnable,
        	                                 'valueS':ruleValue,
                	                         'valueD':value2,
                        	                 'terminalS':ruleType,
                                	         'terminalD':type2,
	                                         'errorMsg':ruleError,
        	                                 'description':ruleDesc,
                                	         'condition':ruleCondition,
	                                         'action':ruleAction,
        	                                 'actionList':actionList[1],
                	                         'PrioritySel':rulePriority,
                                	         'priorityList':priority,
                        	                 'allMappings':RuleTableManager.GetResolverMappings(tableName),
	                                         'ConditionMappings':RuleTableManager.getConditionMappings(),
        	                                 'ActionMappings':RuleTableManager.getActionMappings(),
                	                         'errors': errors,
						 'rule_uuid':ruleid,}
                        	                         )
		else:
			return rule_edit(request, ruleid, tableName, errors)

def enable_disable(request, rule_uuid, table_name):

	RuleTableManager.EnableOrDisableRule(rule_uuid,table_name)

	return HttpResponseRedirect("/policies")	

def condition_create(request, TableName):
	return simple.direct_to_template(request,
                                          template = 'policyEngine/condition_create.html',
                                          extra_context = {'user': request.user,
							   'tableName' : TableName,
							   'mappings' : RuleTableManager.getConditionMappings()},
                                        )

def rule_delete(request, table_name):
	
	rule_uuid = request.POST.get("uuid")
	RuleTableManager.deleteRule(rule_uuid,table_name)

	return HttpResponseRedirect("/policies")
	
def update_ruleTable_policy(request):
	
	policy = request.POST.get("defaultPolicy")
	tableName = request.POST.get("table_name")
	RuleTableManager.UpdateRuleTablePolicy(policy,tableName)
	 
	return HttpResponseRedirect("/policies")

def rule_edit(request,table_name,rule_uuid,errors):

	rule = RuleTableManager.getRuleOrIndexOrIsEnabled(rule_uuid,'Rule',table_name)
	rulevalues = RuleTableManager.getValue(rule)
	ruletypes = RuleTableManager.getType(rule)
	#Flag to be able to diferenciate edit state from creating estate                
        edit = True
	actionList = RuleTableManager.SetActionList(rule,RuleTableManager.getActionMappings())
	priorityList = RuleTableManager.SetPriorityList(rule,table_name)
	error = str(rule.getErrorMsg())
	description = str(rule.getDescription())

	return simple.direct_to_template(request,
                                                 template = 'policyEngine/policy_create.html',
                                                 extra_context = {'user':request.user,
                                                                  'edit':edit,
                                                                  'rule':rule,
                                                                  'priority':RuleTableManager.getRuleOrIndexOrIsEnabled(rule_uuid,'Index',table_name),
								  'enabled':RuleTableManager.getRuleOrIndexOrIsEnabled(rule_uuid,'Enabled',table_name),
                                                                  'valueS':rulevalues[0],
                                                                  'valueD':rulevalues[1],
                                                                  'terminalS':ruletypes[0],
                                                                  'terminalD':ruletypes[1],
                                                                  'rule_uuid':rule_uuid,
								  'ptable':table_name,
								  'errorMsg':error,
								  'description':description,
								  'condition':rule.getConditionDump(),
								  'action':actionList[0],
								  'actionList':actionList[1],
								  'PrioritySel':priorityList[0], 
								  'priorityList':priorityList[1],
								  'allMappings':RuleTableManager.GetResolverMappings(),
								  'ConditionMappings':RuleTableManager.getConditionMappings(),
								  'ActionMappings':RuleTableManager.getActionMappings(),
                                                                  'CurrentTable':table_name,
								  'errors':errors},
                                        )

