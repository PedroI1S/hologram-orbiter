import sys,json,math
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[3]/'Hologram_Orbiter_v3_0'
sys.path.insert(0,str(BASE/'CAD'))
from probe import read_binary_stl
P=json.loads((BASE/'CAD/parameters.json').read_text())

def polygon(p):
    p=np.array(p,float); q=np.roll(p,-1,axis=0); c=p[:,0]*q[:,1]-q[:,0]*p[:,1]
    A=c.sum()/2; Qx=((p[:,0]+q[:,0])*c).sum()/6; Qy=((p[:,1]+q[:,1])*c).sum()/6
    Iyy=((p[:,0]**2+p[:,0]*q[:,0]+q[:,0]**2)*c).sum()/12
    Ixx=((p[:,1]**2+p[:,1]*q[:,1]+q[:,1]**2)*c).sum()/12
    Ixy=((2*p[:,0]*p[:,1]+p[:,0]*q[:,1]+q[:,0]*p[:,1]+2*q[:,0]*q[:,1])*c).sum()/24
    return np.array([A,Qx,Qy,Iyy,Ixx,Ixy])*np.sign(A)

def clip(p,ax,val,gt):
    out=[]
    for a,b in zip(p,p[1:]+p[:1]):
        ina=a[ax]>=val if gt else a[ax]<=val; inb=b[ax]>=val if gt else b[ax]<=val
        if ina:out.append(a)
        if ina!=inb:
            t=(val-a[ax])/(b[ax]-a[ax]);out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
    return out

def box_clip(p,x0,x1,y0,y1):
    for ax,val,gt in [(0,x0,True),(0,x1,False),(1,y0,True),(1,y1,False)]:p=clip(p,ax,val,gt)
    return p

q=P['panel'];outer=q['profile_outer_xy'];inner=q['profile_cavity_xy']
band=box_clip(inner,1.2,4,-7.2,7.2)
channel=box_clip(outer,2,4,-6.2,6.2)
v=polygon(outer)-polygon(inner)+polygon(band)-polygon(channel)
A,Qx,Qy,Iyy,Ixx,Ixy=v;cx=Qx/A;cy=Qy/A
Iyy-=A*cx**2; Ixx-=A*cy**2;Ixy-=A*cx*cy
print('PANEL SECTION:',dict(A_mm2=A,cx_mm=cx,cy_mm=cy,Iyy_mm4=Iyy,Ixx_mm4=Ixx,Ixy_mm4=Ixy,c_outer_mm=4-cx,c_inner_mm=4+cx))
w=0.0445*(60*math.pi)**2*.1/208
for L,E in [(86,2300),(86,2000),(99,2000)]:
    Ieff=Iyy-Ixy**2/Ixx
    M=w*L*L/2
    print('FLEX',dict(L=L,E=E,delta_nominal_I910=w*L**4/(8*E*910),delta_updated_Ieff=w*L**4/(8*E*Ieff),sigma_outer_simple=M*(4-cx)/Iyy,sigma_inner_simple=M*(4+cx)/Iyy))

def massprops(t):
    a,b,c=t[:,0],t[:,1],t[:,2];V=np.einsum('ij,ij->i',a,np.cross(b,c))/6
    s=a+b+c;M=(V[:,None]*s/4).sum(axis=0)
    # integral coordinate products on tetrahedron with fourth vertex at origin
    S=sum(np.einsum('ni,nj->nij',u,u) for u in [a,b,c])+np.einsum('ni,nj->nij',s,s)
    Q=(V[:,None,None]*S/20).sum(axis=0)
    return V.sum(),M,Q

inertias={}
for name in ['01_aranha_ABS.stl','02_painel_LED_ABS_1x.stl','03_tampa_baia_ABS.stl']:
    t=read_binary_stl(BASE/'exports/stl'/name)
    if name.startswith('02'):
        # export rotation y=90: x'=z,y'=y,z'=-x+4
        orig=np.stack([4-t[:,:,2],t[:,:,1],t[:,:,0]],axis=-1)
        orig[:,:,0]+=100;t=orig
    V,M,Q=massprops(t);mass=V*.00104
    Iz=(Q[0,0]+Q[1,1])*.00104/1e6
    inertias[name]=Iz
    print('MASS INERTIA',name,dict(mass_g=mass,cg_mm=(M/V).tolist(),Iz_g_m2=Iz))
led=3*6.2*((103/1000)**2+(.012**2)/12)
hw=3*(2*(.08**2)+2*(.09**2))
battery=50*((.030**2+.058**2)/12)
counter=3.06*.033**2
misc=sum(c['mass_g']*((sum(v*v for v in c.get('center_xy',[0,0]))/1e6) if 'center_xy' in c else (.0357**2)) for c in P['spider']['bay_layout']['components'])
Itotal=inertias['01_aranha_ABS.stl']+3*inertias['02_painel_LED_ABS_1x.stl']+inertias['03_tampa_baia_ABS.stl']+led+hw+battery+counter+misc+.2*.029**2
print('INERTIA_TOTAL_EST',dict(I_g_m2=Itotal,E_j=.5*Itotal/1000*(60*math.pi)**2,led=led,hardware=hw,battery=battery,counter=counter,misc=misc))
omega=60*math.pi;Kt=9.5493/920;I=0.00155
for ramp in [8,12]:
    Tacc=I*omega/ramp;Tdrag=.0514;iph=(Tacc+Tdrag)/Kt
    print('STARTUP',dict(ramp=ramp,Tacc_Nm=Tacc,iph_A=iph,pin_W=Kt*omega*iph+.221*iph**2+.7,source_7V_A=(Kt*omega*iph+.221*iph**2+.7)/7))
iph=4.95*(2000/1800)**2;temp=25+3.5*(.221*iph**2+.7)
print('STRETCH',dict(iph_A=iph,temp_C=temp))
for iph in [3,4,4.44,4.95,5,5.5,6,8]:
    print('STEADY',iph,dict(pin_W=Kt*omega*iph+.221*iph**2+.7,temperature_C=25+3.5*(.221*iph**2+.7)))
print('BALANCE',dict(e_um=6.3/omega*1000,U_gmm=252*6.3/omega))

def slice_props(t,z):
    sums=np.zeros(6)
    for tri in t:
        ints=[]
        for a,b in zip(tri,np.roll(tri,-1,axis=0)):
            if (a[2]<z<b[2]) or (b[2]<z<a[2]):
                f=(z-a[2])/(b[2]-a[2]);ints.append(a+f*(b-a))
        if len(ints)!=2:continue
        a,b=ints
        tangent=np.cross(np.array([0,0,1]),np.cross(tri[1]-tri[0],tri[2]-tri[0]))
        if np.dot(b-a,tangent)<0:a,b=b,a
        x,y=a[:2];X,Y=b[:2];c=x*Y-X*y
        sums+=np.array([c/2,(x+X)*c/6,(y+Y)*c/6,(x*x+x*X+X*X)*c/12,(y*y+y*Y+Y*Y)*c/12,(2*x*y+x*Y+X*y+2*X*Y)*c/24])
    A,Qx,Qy,iyy,ixx,ixy=sums
    return dict(A_mm2=A,cx=Qx/A,cy=Qy/A,Iyy=iyy-Qx*Qx/A,Ixx=ixx-Qy*Qy/A,Ixy=ixy-Qx*Qy/A)
tri=read_binary_stl(BASE/'exports/stl/02_painel_LED_ABS_1x.stl')
tri=np.stack([4-tri[:,:,2],tri[:,:,1],tri[:,:,0]],axis=-1)
for z in [20.23,50.23,90.23]:print('INDEPENDENT_STL_SECTION',z,slice_props(tri,z))
