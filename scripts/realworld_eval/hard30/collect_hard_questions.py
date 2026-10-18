"""Build the 30 application-level real questions and recompute every answer key (sympy / mpmath).

Source: the public compilation "Chuyên đề trong đề thi tốt nghiệp THPT Quốc gia môn Toán 2017-2021" (URL below).
Download it to data/results/pipeline_realworld/hard30/sources/thpt_2017_2021.pdf (git-ignored, third-party document), then
    python scripts/realworld_eval/hard30/collect_hard_questions.py
It writes the 30 questions, their checks and the 100-question set that replaces 30 basic questions of the previous one
(all under data/results/pipeline_realworld/). The question-number and page of every question are in its source_reference.
"""
import csv
import json
import re
import hashlib
from collections import Counter
import sympy as sp
import mpmath as mp
from pathlib import Path
import fitz

REPO = Path(__file__).resolve().parents[3]
HERE = REPO / 'data/results/pipeline_realworld'
OUT = HERE / 'hard30'
Q = HERE / 'questions'
DOC = fitz.open(OUT / 'sources/thpt_2017_2021.pdf')

def blocks(start, stop):
    text = '\n'.join(DOC[i].get_text() for i in range(start-1, stop))
    parts = re.split(r'Câu (\d+)\.', text)
    return {int(parts[i]): parts[i+1] for i in range(1, len(parts), 2)}

URL = 'https://file.montoan.com.vn/file-pdf/chuyen-de-trong-de-thi-tot-nghiep-thpt-quoc-gia-mon-toan-2017-2021.pdf'
TITLE = 'Chuyên đề trong đề thi tốt nghiệp THPT Quốc gia môn Toán 2017–2021'
ROWS = []

def add(topic, kind, page, num, stem, opts, letter, proof, reason, params):
    assert len(opts) == 4 and letter in 'ABCD'
    qid = f'VD-{len(ROWS)+1:03}'
    question = stem + '\n' + '\n'.join(f'{l}. {v}' for l,v in zip('ABCD',opts))
    ROWS.append(dict(id=qid, topic=topic, question_markdown_latex=question,
        answer_markdown_latex=f'{letter}. {opts["ABCD".index(letter)]}', answer_letter=letter,
        dang_dung=str(kind), source_url=URL+f'#page={page}', source_title=TITLE,
        source_reference=f'Chuyên đề {2 if topic.startswith("Mũ") else 4}; câu {num}; trang PDF {page}; trang in {page-1}',
        difficulty='Vận dụng' if kind in [62,68,123,126,132,135] else 'Vận dụng cao',
        difficulty_note='Mức độ do người rà soát đánh giá theo số bước và nội dung; không phải nhãn in trong tuyển tập.',
        solution_check=proof, scope_reason=reason, params=params,
        transcription_note='Đối chiếu ảnh trang PDF; chỉ chuẩn hóa công thức sang Markdown LaTeX, giữ số liệu và thứ tự A–D.'))

def collect():
    ml='Mũ–Logarit'; sc='Số phức'
    reason='Đặt t=a^x>0; đếm m nguyên để phương trình bậc hai theo t có hai nghiệm dương phân biệt (Dạng 62).'
    add(ml,62,76,78,r'Gọi $S$ là tập hợp tất cả các giá trị nguyên của tham số $m$ sao cho phương trình $16^x-m\cdot4^{x+1}+5m^2-45=0$ có hai nghiệm phân biệt. Hỏi $S$ có bao nhiêu phần tử?',
        ['$13$','$3$','$6$','$4$'],'B',r'Đặt $t=4^x>0$: $t^2-4mt+5m^2-45=0$. Điều kiện $\Delta>0,S>0,P>0$ cho $m>3$ và $m<\sqrt{45}$. Các số nguyên là $4,5,6$, có 3.',reason,dict(group='exp_roots',a=4,k=4,c=5,d=45,answer=3))
    add(ml,62,77,96,r'Gọi $S$ là tập hợp các giá trị nguyên của tham số $m$ sao cho phương trình $9^x-m\cdot3^{x+1}+3m^2-75=0$ có hai nghiệm phân biệt. Hỏi $S$ có bao nhiêu phần tử?',
        ['$8$','$4$','$19$','$5$'],'B',r'Đặt $t=3^x>0$: $t^2-3mt+3m^2-75=0$. Điều kiện là $m>5$ và $m<10$; nhận $m=6,7,8,9$, có 4.',reason,dict(group='exp_roots',a=3,k=3,c=3,d=75,answer=4))
    reason='Hai lôgarit cơ số biến cộng bằng 2; dùng đổi cơ số và bất đẳng thức để suy ra quan hệ a,b, rồi tính a+2b (Dạng 63).'
    for page,num,p,alpha,beta,opts,letter,ans in [
        (76,79,3,3,2,['$6$','$9$',r'$\frac72$',r'$\frac52$'],'C',sp.Rational(7,2)),
        (77,91,4,4,5,['$9$','$6$',r'$\frac{27}{4}$',r'$\frac{20}{3}$'],'C',sp.Rational(27,4)),
        (77,98,2,2,2,[r'$\frac{15}{4}$','$5$','$4$',r'$\frac32$'],'A',sp.Rational(15,4))]:
        stem=rf'Cho $a>0,b>0$ thỏa mãn $\log_{{{alpha}a+{beta}b+1}}({p*p}a^2+b^2+1)+\log_{{{2*p}ab+1}}({alpha}a+{beta}b+1)=2$. Giá trị của $a+2b$ bằng'
        aa=sp.Rational(alpha+beta*p,2*p*p); bb=p*aa
        proof=rf'Đặt $A={p*p}a^2+b^2+1$, $B={2*p}ab+1$, $L={alpha}a+{beta}b+1$. Có $A\ge B>1$. Với $t=\log_B L>0$, phương trình cho $\log_B A=2t-t^2\le1$. Do đó $A=B=L$, suy ra $b={p}a$, $a={sp.latex(aa)}$, $b={sp.latex(bb)}$ và $a+2b={sp.latex(ans)}$.'
        add(ml,63,page,num,stem,opts,letter,proof,reason,dict(group='double_log',p=p,alpha=alpha,beta=beta,answer=str(ans)))
    reason='Đếm m nguyên trong khoảng để phương trình a^x+m=log_a(x-m) có nghiệm, dùng tính đơn điệu của hai hàm ngược (Dạng 64).'
    for page,num,a,H,opts,letter in [
        (76,80,5,20,['$20$','$19$','$9$','$21$'],'B'),
        (77,92,7,25,['$9$','$25$','$24$','$26$'],'C'),
        (77,97,2,18,['$9$','$19$','$17$','$18$'],'C')]:
        stem=rf'Cho phương trình ${a}^x+m=\log_{a}(x-m)$ với $m$ là tham số. Có bao nhiêu giá trị nguyên của $m\in(-{H};{H})$ để phương trình đã cho có nghiệm?'
        proof=rf'Đặt $f(x)={a}^x+m$, là hàm tăng từ $\mathbb R$ lên $(m,+\infty)$. Phương trình $f(x)=f^{{-1}}(x)$ tương đương $f(x)=x$: nếu $f(x)>x$ hoặc $f(x)<x$ thì áp dụng f dẫn đến mâu thuẫn với $f(f(x))=x$. Vì vậy $m=x-{a}^x$. Giá trị lớn nhất $M=-\log_{a}(\ln {a})-1/\ln {a}$ thuộc $(-1;0)$. Các m nguyên nhận $-{H-1},\ldots,-1$, có {H-1}.'
        add(ml,64,page,num,stem,opts,letter,proof,reason,dict(group='inverse',a=a,H=H,answer=H-1))
    reason='Đếm m nguyên để phương trình log_9(x^2)-log_3(kx-1)=-log_3 m có nghiệm; cùng điều kiện và phép biến đổi Dạng 68.'
    for page,num,k,opts,letter in [
        (78,112,3,['$2$','$4$','$3$','Vô số.'],'A'),
        (79,126,5,['Vô số.','$5$','$4$','$6$'],'C'),
        (80,133,4,['$5$','$3$','Vô số.','$4$'],'B')]:
        stem=rf'Cho phương trình $\log_9(x^2)-\log_3({k}x-1)=-\log_3m$ ($m$ là tham số thực). Có tất cả bao nhiêu giá trị nguyên của $m$ để phương trình đã cho có nghiệm?'
        proof=rf'Điều kiện $x>1/{k},m>0$. Khi đó $\log_9(x^2)=\log_3 x$, nên $mx={k}x-1$ và $x=1/({k}-m)$. Điều kiện tương đương $0<m<{k}$: có {k-1} số nguyên.'
        add(ml,68,page,num,stem,opts,letter,proof,reason,dict(group='log_parameter',k=k,answer=k-1))
    reason='Đếm m nguyên dương để tích tam thức theo log x và căn(a^x-m) bằng 0 có đúng hai nghiệm; phải tính cả nghiệm do căn bằng 0 (Dạng 69).'
    for page,num,base,a,poly,low,high,opts,letter,ans in [
        (79,113,2,7,r'4\log_2^2x+\log_2x-5',2**(-sp.Rational(5,4)),sp.Integer(2),['$49$','$47$','Vô số.','$48$'],'B',47),
        (79,127,3,5,r'2\log_3^2x-\log_3x-1',1/sp.sqrt(3),sp.Integer(3),['$123$','$125$','Vô số.','$124$'],'A',123),
        (80,134,3,4,r'2\log_3^2x-\log_3x-1',1/sp.sqrt(3),sp.Integer(3),['Vô số.','$62$','$63$','$64$'],'B',62)]:
        stem=rf'Cho phương trình $({poly})\sqrt{{{a}^x-m}}=0$ ($m$ là tham số thực). Có tất cả bao nhiêu giá trị nguyên dương của $m$ để phương trình đã cho có đúng hai nghiệm phân biệt?'
        U=a**high
        proof=rf'Hai nghiệm của thừa số lôgarit là $u={sp.latex(low)}$, $v={sp.latex(high)}$. Với cả ba câu này, $2<{a}^u<3$ và ${a}^v={U}$. Khi $m=1$ có đúng hai nghiệm $u,v$ (nghiệm từ căn là x=0, không thuộc miền log). Khi $m=2$ có ba nghiệm. Khi $3\le m<{U}$ có hai nghiệm $v,\log_{a}m$. Khi $m\ge {U}$ chỉ có một nghiệm. Do đó có $1+({U}-3)={ans}$ giá trị.'
        add(ml,69,page,num,stem,opts,letter,proof,reason,dict(group='product_radical',base=base,a=a,low=str(low),high=str(high),answer=ans))
    reason='Đếm x nguyên để số y nguyên thỏa bất phương trình giữa log(x^2+y) và log(x+y) không quá K; quy về đếm t=x+y (Dạng 73).'
    for page,num,A,B,K,opts,letter,ans,lo,hi,T in [
        (81,159,4,3,728,['$59$','$58$','$116$','$115$'],'C',116,-57,58,3367),
        (82,176,3,2,127,['$89$','$46$','$45$','$90$'],'D',90,-44,45,2059),
        (83,185,3,2,255,['$80$','$79$','$157$','$158$'],'D',158,-78,79,6305)]:
        stem=rf'Có bao nhiêu số nguyên $x$ sao cho ứng với mỗi $x$ có không quá {K} số nguyên $y$ thỏa mãn $\log_{A}(x^2+y)\ge\log_{B}(x+y)$?'
        proof=rf'Đặt $t=x+y\in\mathbb Z_{{>0}}$, $c=x(x-1)\ge0$. Điều kiện là $t+c\ge t^r$, $r=\log_{B}{A}>1$. Hàm $t^r-t$ tăng nghiêm ngặt trên $[1,+\infty)$. Số nghiệm t không quá {K} khi và chỉ khi $c<({K+1})^r-({K+1})={T}$. Suy ra ${lo}\le x\le {hi}$, có {ans} số nguyên. Hai miền log tự thỏa vì t>=1,c>=0.'
        add(ml,73,page,num,stem,opts,letter,proof,reason,dict(group='nested_count',A=A,B=B,K=K,T=T,lo=lo,hi=hi,answer=ans))
    add(sc,123,120,37,r'Có bao nhiêu số phức $z$ thỏa mãn $|z+3i|=\sqrt{13}$ và $\frac{z}{z+2}$ là số thuần ảo?',
        ['Vô số.','$2$','$0$','$1$'],'D',r'Đặt z=x+yi, z khác -2. Hai phương trình là $x^2+(y+3)^2=13$ và $x^2+y^2+2x=0$. Trừ nhau cho $x=3y-2$. Thế vào được $2y(5y-3)=0$. Giao điểm $z=-2$ bị loại do mẫu bằng 0; còn $z=-1/5+3i/5$, thương bằng i/3. Có một số phức.',
        'Giao hai đường tròn do điều kiện môđun và phân thức thuần ảo, đếm số phức và loại cực của phân thức (Dạng 123).',dict(group='circle_imag',answer=1))
    reason='Đếm nghiệm phương trình chứa môđun |z|(z-c-i)+2i=(c+1-i)z; đặt r=|z| và kiểm tra nghiệm r (Dạng 126).'
    for page,num,c,opts,letter in [(120,51,4,['$2$','$3$','$1$','$4$'],'B'),(121,59,6,['$2$','$3$','$1$','$4$'],'B'),(121,63,5,['$1$','$3$','$4$','$2$'],'B')]:
        stem=rf'Có bao nhiêu số phức $z$ thỏa mãn $|z|(z-{c}-i)+2i=({c+1}-i)z$?'
        proof=rf"""Đặt $r=|z|\ge0$. Biến đổi phương trình được $[r-({c+1})+i]z=cr+i(r-2)$; hệ số này không bằng 0 vì phần ảo bằng 1. Với mỗi $r$, có duy nhất $z=\frac{{cr+i(r-2)}}{{r-({c+1})+i}}$. Điều kiện $|z|=r$ tương đương $r^2((r-c-1)^2+1)=c^2r^2+(r-2)^2$, hay $(r-1)q(r)=0$ với $q(r)=r^3-(2c+1)r^2+4$. Với từng $c=4,5,6$, ta có $q(0)=4>0$, $q(1)=4-2c<0$ và $q(r)\to+\infty$. Đạo hàm $q'(r)=r(3r-4c-2)$ cho thấy $q$ giảm đến $r=(4c+2)/3$ rồi tăng. Vì vậy $q$ có đúng hai nghiệm dương, một thuộc $(0,1)$ và một lớn hơn 1. Cộng với nghiệm $r=1$, phương trình có đúng ba giá trị $r>0$, mỗi giá trị cho một số phức $z$."""
        add(sc,126,page,num,stem,opts,letter,proof,reason,dict(group='modulus_equation',c=c,answer=3))
    reason='Biến đổi quỹ tích |z|=sqrt(2) qua w=(a+iz)/(1+z), tìm bán kính đường tròn w (Dạng 132).'
    for page,num,a,opts,letter in [(122,73,4,[r'$\sqrt{34}$','$26$','$34$',r'$\sqrt{26}$'],'A'),(122,83,2,['$10$',r'$\sqrt2$','$2$',r'$\sqrt{10}$'],'D'),(123,88,5,['$52$',r'$2\sqrt{13}$',r'$2\sqrt{11}$','$44$'],'B')]:
        stem=rf'Xét các số phức $z$ thỏa mãn $|z|=\sqrt2$. Trên mặt phẳng tọa độ $Oxy$, tập hợp điểm biểu diễn các số phức $w=\frac{{{a}+iz}}{{1+z}}$ là một đường tròn có bán kính bằng'
        proof=rf'Đảo biến đổi được $z=({a}-w)/(w-i)$. Với w=u+vi, điều kiện là $(u-{a})^2+v^2=2(u^2+(v-1)^2)$, tức $(u+{a})^2+(v-2)^2={2*(a*a+1)}$. w=i không thuộc đường tròn và z=-1 không thuộc đường tròn ban đầu; vì thế phép đổi không làm mất điểm nào của quỹ tích. Bán kính là ${sp.latex(sp.sqrt(2*(a*a+1)))}$.'
        add(sc,132,page,num,stem,opts,letter,proof,reason,dict(group='mobius',a=a,answer=str(sp.sqrt(2*(a*a+1)))))
    reason='Đếm m thực để phương trình z^2-2(m+1)z+m^2=0 có một nghiệm môđun R; tách nghiệm thực và nghiệm liên hợp (Dạng 135).'
    for page,num,R,opts,letter in [(125,141,7,['$2$','$3$','$1$','$4$'],'B')]:
        stem=rf'Trên tập hợp số phức, xét phương trình $z^2-2(m+1)z+m^2=0$ ($m$ là tham số thực). Có bao nhiêu giá trị của $m$ để phương trình đó có nghiệm $z_0$ thỏa mãn $|z_0|={R}$?'
        proof=rf'Nếu $2m+1<0$, hai nghiệm liên hợp có môđun |m|; nhận $m=-{R}$. Nếu $2m+1\ge0$, nghiệm thực có môđun {R} phải bằng ±{R}. Thế z={R} cho $m={R}\pm\sqrt{{{2*R}}}$ (đều thỏa điều kiện). Thế z=-{R} cho phương trình m có biệt thức âm. Ba giá trị khác nhau, tổng là 3.'
        add(sc,135,page,num,stem,opts,letter,proof,reason,dict(group='root_modulus',R=R,answer=3))
    reason='Cho |z|,|w| cố định; khi |z+i liên hợp(w)+C| nhỏ nhất thì tính |z-w| bằng điều kiện dấu bằng bất đẳng thức tam giác (Dạng 141).'
    for page,num,C,ctext,opts,letter,ans in [
        (125,142,-6-8j,'-6-8i',[r'$\frac{\sqrt{221}}5$',r'$\sqrt5$','$3$',r'$\frac{\sqrt{29}}5$'],'D',sp.sqrt(29)/5),
        (126,153,-6+8j,'-6+8i',['$3$',r'$\frac{\sqrt{29}}5$',r'$\sqrt5$',r'$\frac{\sqrt{221}}5$'],'D',sp.sqrt(221)/5)]:
        stem=rf'Xét các số phức $z,w$ thỏa mãn $|z|=1$ và $|w|=2$. Khi $|z+i\overline{{w}}{ctext}|$ đạt giá trị nhỏ nhất, $|z-w|$ bằng'
        zr=sp.Rational(-int(C.real),10); zi=sp.Rational(-int(C.imag),10)
        # i*conjugate(w)=2z -> w=2i*conjugate(z).
        wr=2*zi; wi=2*zr
        proof=rf'Đặt $C={ctext}$, |C|=10. Bất đẳng thức tam giác cho giá trị nhỏ nhất 10-1-2=7; dấu bằng buộc $z=-C/10$ và $i\overline w=-2C/10=2z$. Suy ra $z={sp.latex(zr+sp.I*zi)}$, $w={sp.latex(wr+sp.I*wi)}$, $|z-w|={sp.latex(ans)}$. Các giá trị này đạt dấu bằng nên cực tiểu tồn tại.'
        add(sc,141,page,num,stem,opts,letter,proof,reason,dict(group='two_complex',Cr=int(C.real),Ci=int(C.imag),answer=str(ans)))
    for page,num,k,term,opts,letter in [(127,166,-4,'-4az',['$3$','$2$','$1$','$4$'],'A'),
                                       (128,178,2,'+2az',['$2$','$3$','$1$','$4$'],'B'),
                                       (129,184,-2,'-2az',['$2$','$1$','$4$','$3$'],'D')]:
        ar=sp.Rational(-9,2*k); ac=sp.Rational(-2,k)
        proof=rf'Hệ số thực nên hai nghiệm hoặc đều thực hoặc liên hợp. Nếu đều thực, quan hệ cho $z_1=3,z_2=3/2$; Viète cho $a={sp.latex(ar)},b=\pm\sqrt{{5/2}}$, có 2 cặp. Nếu liên hợp không thực, đặt $z_1=s+ti,z_2=s-ti$; quan hệ cho $s+2t=3,t+2s=3$, suy ra s=t=1. Viète cho $a={sp.latex(ac)},b=0$, thêm 1 cặp. Tổng 3 cặp. Hai trường hợp loại trừ nhau và bao quát mọi nghiệm của đa thức hệ số thực.'
        add(sc,136,page,num,rf'Trên tập hợp số phức, xét phương trình $z^2{term}+b^2+2=0$ ($a,b$ là các tham số thực). Có bao nhiêu cặp số thực $(a;b)$ sao cho phương trình đó có hai nghiệm $z_1,z_2$ thỏa mãn $z_1+2iz_2=3+3i$?',
            opts,letter,proof,'Cùng hệ dữ kiện đa thức bậc hai hệ số thực, quan hệ z1+2iz2 và yêu cầu đếm cặp (a,b) của Dạng 136; thay hệ số của az, không đổi phương pháp.',dict(group='root_pair',k=k,answer=3))

def verify_math(r):
    p=r['params']; g=p['group']
    if g=='exp_roots':
        # Solve the substituted quadratic directly, then test both roots positive.
        t=sp.Symbol('t'); good=[]
        for m in range(-200,201):
            roots=sp.solve(t*t-p['k']*m*t+p['c']*m*m-p['d'],t)
            if len(roots)==2 and all(v.is_real and v>0 for v in roots): good.append(m)
        assert len(good)==p['answer'] and all(abs(m)<199 for m in good)
    elif g=='double_log':
        a=sp.Rational(p['alpha']+p['beta']*p['p'],2*p['p']**2); b=p['p']*a
        A=p['p']**2*a*a+b*b+1; B=2*p['p']*a*b+1; L=p['alpha']*a+p['beta']*b+1
        assert A==B==L and A>1 and a+2*b==sp.sympify(p['answer'])
    elif g=='inverse':
        mp.mp.dps=80; a=p['a']; M=-mp.log(mp.log(a))/mp.log(a)-1/mp.log(a)
        assert -1<M<0 and len([m for m in range(-p['H']+1,p['H']) if m<=M])==p['answer']
    elif g=='log_parameter':
        k=p['k']; good=[]
        for m in range(-100,101):
            if m>0 and k!=m:
                x=sp.Rational(1,k-m)
                if x>sp.Rational(1,k):
                    assert sp.simplify(x/(k*x-1))-sp.Rational(1,m)==0
                    good.append(m)
        assert len(good)==p['answer']
    elif g=='product_radical':
        mp.mp.dps=80; low=mp.mpf(str(sp.N(sp.sympify(p['low']),75))); high=mp.mpf(p['high'])
        a=p['a']; assert 2<mp.power(a,low)<3
        count=0
        for m in range(1,1001):
            roots=[v for v in [low,high] if mp.power(a,v)>=m-mp.mpf('1e-65')]
            s=mp.log(m)/mp.log(a)
            if s>0 and not any(abs(s-v)<mp.mpf('1e-60') for v in roots): roots.append(s)
            if len(roots)==2: count+=1
        assert count==p['answer']
    elif g=='nested_count':
        # Exact exponent identity at K+1, then direct logarithm test for t=K+1
        # on an independently bounded integer-x range.
        mp.mp.dps=80; t=p['K']+1
        exact_power=mp.power(t,mp.log(p['A'])/mp.log(p['B']))
        assert abs(exact_power-(t+p['T']))<mp.mpf('1e-65')
        xs=[x for x in range(-1000,1001) if mp.log(t+x*x-x)/mp.log(p['A'])<mp.log(t)/mp.log(p['B'])-mp.mpf('1e-65')]
        assert xs==list(range(p['lo'],p['hi']+1)) and len(xs)==p['answer']
    elif g=='circle_imag':
        x,y=sp.symbols('x y',real=True)
        sols=sp.solve([x*x+(y+3)**2-13,x*x+y*y+2*x],[x,y])
        valid=[(a,b) for a,b in sols if (a,b)!=(-2,0)]
        assert len(valid)==1 and sp.simplify((valid[0][0]+sp.I*valid[0][1])/(valid[0][0]+2+sp.I*valid[0][1]))==sp.I/3
    elif g=='modulus_equation':
        t=sp.Symbol('t'); c=p['c']
        f=sp.Poly(c*c*t*t+(t-2)**2-t*t*((t-c-1)**2+1),t)
        expected=sp.Poly(-(t-1)*(t**3-(2*c+1)*t**2+4),t)
        q=sp.Poly(t**3-(2*c+1)*t**2+4,t)
        assert f==expected and q.count_roots(0,sp.oo)==2
        assert q.eval(1)==4-2*c<0 and f.count_roots(0,sp.oo)==3
        assert p['answer']==3
    elif g=='mobius':
        a=p['a']; assert sp.sympify(p['answer'])**2==2*(a*a+1)
        # Direct image of 3 points determines circle, independently of equation expansion.
        points=[]
        for z in [sp.sqrt(2),-sp.sqrt(2),sp.I*sp.sqrt(2)]:
            w=sp.simplify((a+sp.I*z)/(1+z)); points.append(sp.Point(sp.re(w),sp.im(w)))
        assert sp.simplify(sp.Circle(*points).radius**2-2*(a*a+1))==0
    elif g=='root_modulus':
        R=p['R']; vals=[-R,R-sp.sqrt(2*R),R+sp.sqrt(2*R)]
        assert len(set(vals))==3
        for m in vals:
            roots=[m+1+sp.sqrt(2*m+1),m+1-sp.sqrt(2*m+1)]
            assert any(sp.sqrtdenest(sp.simplify(z*sp.conjugate(z)-R*R))==0 for z in roots)
    elif g=='two_complex':
        C=p['Cr']+sp.I*p['Ci']; z=-C/10; w=2*sp.I*sp.conjugate(z)
        assert sp.simplify(sp.Abs(z))==1 and sp.simplify(sp.Abs(w))==2
        assert sp.simplify(sp.Abs(z+sp.I*sp.conjugate(w)+C))==7
        assert sp.simplify(sp.Abs(z-w)-sp.sympify(p['answer']))==0
    elif g=='root_pair':
        # Independent elimination in real/imaginary coordinates, without choosing
        # the real-root / conjugate-root cases used in the written proof.
        s,t,u,v,a,b=sp.symbols('s t u v a b',real=True)
        z1=s+sp.I*t; z2=u+sp.I*v
        solutions=sp.solve([s-2*v-3,t+2*u-3,s+u+p['k']*a,t+v,
            s*u-t*v-b*b-2,s*v+t*u],[s,t,u,v,a,b],dict=True)
        assert len(solutions)==p['answer']==3
        for sol in solutions:
            assert sp.simplify((z1+2*sp.I*z2-3-3*sp.I).subs(sol))==0
            assert all(sp.simplify((z*z+p['k']*a*z+b*b+2).subs(sol))==0 for z in [z1,z2])
    else: raise ValueError(g)

def write_csv(path, rows, fields):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def export():
    assert len(ROWS)==30
    for r in ROWS: verify_math(r)
    fields=['id','topic','question_markdown_latex','answer_markdown_latex','answer_letter','dang_dung','source_url','source_title']
    write_csv(Q/'cau_hoi_VD_VDC_30_cau_THPT.csv', ROWS, fields+['difficulty','source_reference'])
    write_csv(OUT/'kiem_tra_30_cau.csv', ROWS, fields+['source_reference','difficulty','difficulty_note','solution_check','scope_reason','transcription_note'])
    (OUT/'30_cau_nguon_va_kiem_tra.json').write_text(json.dumps(ROWS,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# 30 câu vận dụng và vận dụng cao bổ sung','', 'Đề và thứ tự A–D được đối chiếu với ảnh PDF; đáp án được giải lại. Mức độ là đánh giá của người rà soát.','']
    for r in ROWS:
        md += [f'## {r["id"]} — {r["topic"]} — Dạng {r["dang_dung"]}', '', r['question_markdown_latex'],'', '**Đáp án:** '+r['answer_markdown_latex'],'',f'**Nguồn:** [{r["source_reference"]}]({r["source_url"]})','', '**Kiểm tra:** '+r['solution_check'],'']
    (OUT/'cau_hoi_VD_VDC_30_cau_THPT.md').write_text('\n'.join(md),encoding='utf-8')
    # Preserve original 100. Replace a balanced subset of simple questions only.
    original=list(csv.DictReader(open(Q/'cau_hoi_thuc_te_100_cau_da_ra_soat.csv',encoding='utf-8-sig',newline='')))
    easy_ml={1,2,3,4,6,9,10,15,17,23,26,27,28,30,31,32,33,37,38,39,43,44,45,46,49,50,54,55,57,59,61,65,66,67,70,71,74,75,76,79,80,81,84,85,86}
    easy_sp=set(range(89,119))
    remove=[]; needed={'Mũ–Logarit':17,'Số phức':13}
    for r in original:
        n=int(re.search(r'\d+',r['dang_dung']).group())
        if needed[r['topic']]>0 and n in (easy_ml if r['topic'].startswith('Mũ') else easy_sp):
            remove.append(r);needed[r['topic']]-=1
    assert all(v==0 for v in needed.values()), needed
    removed_ids={r['id'] for r in remove}
    final=[r for r in original if r['id'] not in removed_ids]+ROWS
    assert len(final)==100 and len({r['id'] for r in final})==100
    assert Counter(r['topic'] for r in final)==Counter(r['topic'] for r in original)
    write_csv(Q/'cau_hoi_thuc_te_100_cau_tang_30_cau_kho.csv',final,fields)
    changes=[]
    for topic in ['Mũ–Logarit','Số phức']:
        for old,new in zip([r for r in remove if r['topic']==topic],[r for r in ROWS if r['topic']==topic]):
            changes.append(dict(id_bo=old['id'],dang_bo=old['dang_dung'],id_them=new['id'],dang_them=new['dang_dung'],topic=topic,ly_do='Thay câu cơ bản bằng câu vận dụng/vận dụng cao đã giải lại; không sửa file 100 câu gốc.'))
    write_csv(OUT/'30_cau_thay_the.csv',changes,list(changes[0]))
    summary=dict(total_new=30,topics=dict(Counter(r['topic'] for r in ROWS)),types=dict(Counter(r['dang_dung'] for r in ROWS)),final_total=len(final),original_100_sha256=hashlib.sha256((Q/'cau_hoi_thuc_te_100_cau_da_ra_soat.csv').read_bytes()).hexdigest())
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    collect()
    export()
