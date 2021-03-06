import os
from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from user_profile.models import UserProfile

from .models import Problem
from .models import Answerlog
from django.template import Context

from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse

from django.contrib.auth.decorators import login_required
from ratelimit.decorators import ratelimit

from testsite.views import set_rank

class Counter:
	def __init__(self):
		self.count = 0
	
	def increment(self):
		self.count += 1
	
	def setzero(self):
		self.count = 0

def all_problem_test(request):
	problems = Problem.objects.all()
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'test': request})
	return render(request, '_all_problems.html', context)

@login_required(login_url='/login/')
def problem_view(request):
	state = False
	problem_num = request.GET['pnum']
	problem = Problem.objects.get(num=problem_num)
	if problem.tags is not None:
		problem_tags = problem.tags.split('#')[1:]
		for i in range(0, len(problem_tags)):
			problem_tags[i] = problem_tags[i].strip()
		blank_number = 5 - len(problem_tags)
	else:
		problem_tags = ""
		blank_number = 5
	if request.user.is_active:
		current_user = request.user.id
		user_level = UserProfile.objects.get(user_id=current_user).level
		right_problems = UserProfile.objects.get(user_id=current_user).right_problems.split(',')
		solve_user_list = []
		if problem.solve_user is None or problem.solve_user == '':
			solve_user_list.append("No one solved.")
		else:
			solve_users = problem.solve_user.split(',')
			for i in range(0, len(solve_users) - 1):
				solveuser = User.objects.get(id=solve_users[i])
				solve_user_list.append(solveuser.username)
		for i in range(0, len(right_problems) - 1):
			if int(right_problems[i]) == problem.num:
				state = True
				break
		context = Context({'problem': problem, 'test': request, 'user_level': user_level, 'state': state, 'problem_tags': problem_tags, 'blank': blank_number, 'solve_users': solve_user_list})
	else:
		context = Context({'problem': problem, 'test': request, 'problem_tags': problem_tags, 'blank': blank_number})
	return render(request, 'problem_view.html', context)

@login_required(login_url='/login/')
def problem_write(request):
	context = Context({})
	if not request.user.is_staff:
		return HttpResponseRedirect('/')
	return render(request, 'problem_write.html', context)

def problem_write_done(request):
	context = Context({})
	if not request.user.is_staff:
		return HttpResponseRedirect('/')
	if request.method == "GET":
		return render(request, 'problem_write.html', context)
	if request.method == "POST":
		if 'uploadfile' in request.FILES:
			problem = Problem(title = request.POST['title'], created_date = datetime.now(), content = request.POST['content'], author_id = request.user.id, level = request.POST['level'], artifact = request.POST['artifact'], right_answer = request.POST['right_answer'], corrects = 0, submits = 0, score = request.POST['score'], tags = request.POST['tags'], importance = request.POST['importance'], difficulty = request.POST['difficulty'], downfile = request.FILES['uploadfile'])
			problem.save()
		else:
			return render(request, 'problem_write.html', context)
	return render(request, 'problem_write_done.html', context)

@login_required(login_url='/login/')
def problem_download(request):
	if not request.user.is_active:
		return HttpResponseRedirect('/login_check/')
	problem_num = request.GET['pnum']
	problem = Problem.objects.get(num=problem_num)
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	fp = open(os.path.join(BASE_DIR, 'media')+'/'+str(problem.downfile), 'r')
	response = StreamingHttpResponse(fp, content_type='application/force-download')
	response['Content-Disposition'] = 'attachment; filename="%s"' % str(problem.downfile)
	return response

@ratelimit(key='ip', rate='1/30s', block=True)
def problem_answercheck(request):
	try:
		problem_num = request.GET['pnum']
		problem = Problem.objects.get(num=problem_num)
		answer = request.POST['answer']
	except:
		return HttpResponseRedirect('/')

	if answer is None:
		return HttpResponseRedirect('/')

	rights = UserProfile.objects.get(user_id=request.user.id).right_problems.split(',')

	for i in range(0, len(rights) - 1):
		if problem.num == int(rights[i]):
			context = Context({'problem_num': problem.num})
			return render(request, 'problem_solved.html', context)

	answerlog = Answerlog(submitter_id = request.user.id, submit_answer = answer, problem_num = problem.num, problem_title = problem.title)
	answerlog.save()
	UserProfile.objects.filter(user_id=request.user.id).update(last_submit = datetime.now())

	Problem.objects.filter(num=problem_num).update(submits = problem.submits + 1)

	if problem.right_answer.lower() == answer.lower():
		Problem.objects.filter(num=problem_num).update(corrects = problem.corrects + 1)
		if not request.user.is_staff:
			if problem.solve_user is None:
				Problem.objects.filter(num=problem_num).update(solve_user = str(request.user.id) + ',')
			else:
				Problem.objects.filter(num=problem_num).update(solve_user = str(problem.solve_user) + str(request.user.id) + ',')
		profile = UserProfile.objects.get(user_id=request.user.id)
		UserProfile.objects.filter(user_id=request.user.id).update(right_problems = profile.right_problems + str(problem_num) +',')
		if not request.user.is_staff:
			UserProfile.objects.filter(user_id=request.user.id).update(score = profile.score + problem.score)
		set_rank()
		state = True
	else:
		state = False

	context = Context({'problem_num': problem_num, 'state': state})
	return render(request, 'problem_answercheck.html', context)

def artifact1(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="1").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="1").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="1").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="1").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=1 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=1 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="1").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact1/list.html', context)

def artifact2(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="2").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="2").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="2").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="2").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=2 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=2 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="2").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact2/list.html', context)

def artifact3(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="3").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="3").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="3").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="3").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=3 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=3 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="3").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact3/list.html', context)

def artifact4(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="4").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="4").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="4").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="4").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=4 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=4 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="4").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact4/list.html', context)

def artifact5(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="5").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="5").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="5").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="5").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=5 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=5 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="5").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact5/list.html', context)

def artifact6(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="6").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="6").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="6").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="6").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=6 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=6 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="6").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact6/list.html', context)

def artifact7(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="7").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="7").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="7").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="7").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=7 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=7 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="7").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact7/list.html', context)

def artifact8(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="8").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="8").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="8").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="8").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=8 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=8 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="8").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact8/list.html', context)

def artifact9(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="9").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="9").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="9").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="9").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=9 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=9 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="9").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact9/list.html', context)

def artifact10(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="10").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="10").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="10").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="10").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=10 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=10 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="10").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact10/list.html', context)

def artifact11(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="11").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="11").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="11").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="11").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=11 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=11 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="11").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact11/list.html', context)

def artifact12(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="12").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="12").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="12").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="12").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=12 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=12 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="12").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact12/list.html', context)

def artifact13(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="13").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="13").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="13").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="13").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=13 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=13 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="13").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'artifact13/list.html', context)

def anti1(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="14").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="14").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="14").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="14").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=14 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=14 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="14").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'anti1/list.html', context)

def anti2(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="15").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="15").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="15").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="15").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=15 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=15 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="15").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'anti2/list.html', context)

def anti3(request):
	orderby = request.GET.get('orderby')
	if orderby is None:
		orderby = 'title'

	if str(orderby) == "title":
		problems = Problem.objects.filter(artifact="16").order_by("title")
	elif str(orderby) == "rtitle":
		problems = Problem.objects.filter(artifact="16").order_by("-title")
	elif str(orderby) == "level":
		problems = Problem.objects.filter(artifact="16").order_by("level")
	elif str(orderby) == "rlevel":
		problems = Problem.objects.filter(artifact="16").order_by("-level")
	elif str(orderby) == "stats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=16 order by CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)')
	elif str(orderby) == "rstats":
		problems = Problem.objects.raw('select * from problem_problem where artifact=16 order by (CAST(corrects AS float) / (case when submits=0 then CAST(1 AS float) else CAST(submits AS float) end)) DESC')
	else:
		problems = Problem.objects.filter(artifact="16").order_by("title")
	tcounter = Counter()
	context = Context({'problems': problems, 'counter': tcounter, 'request': request})
	return render(request, 'anti3/list.html', context)

def case1(request):
	if not request.user.is_active:
		return HttpResponseRedirect('/login_check/')
	context = Context({})
	return render(request, 'case1/list.html', context)

def case2(request):
	if not request.user.is_active:
		return HttpResponseRedirect('/login_check/')
	context = Context({})
	return render(request, 'case2/list.html', context)

def case3(request):
	if not request.user.is_active:
		return HttpResponseRedirect('/login_check/')
	context = Context({})
	return render(request, 'case3/list.html', context)

def case4(request):
	if not request.user.is_active:
		return HttpResponseRedirect('/login_check/')
	context = Context({})
	return render(request, 'case4/list.html', context)
