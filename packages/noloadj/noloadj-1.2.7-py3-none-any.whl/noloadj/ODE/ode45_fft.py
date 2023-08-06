from noloadj.ODE.ode45 import *
from noloadj.ODE.ode45 import _odeint45

def odeint45_fft(f,x0,t,*P,M,T=0.,h0=1e-5,tol=1.48e-8):
    return _odeint45_fft(f,h0,tol,M,x0,t,T,*P)


@partial(custom_jvp,nondiff_argnums=(0,1,2,3))
def _odeint45_fft(f,h0,tol,M,x0,t,T,*P):

    xs,ys=_odeint45(f,h0,tol,x0,t,T,*P)
    xfft=np.fft.fft(xs,M)*2/M # fft avec normalisation
    xfft=xfft.at[:,0].divide(2)
    module,phase=np.abs(xfft),np.angle(xfft) # amplitude et phase de la fft
    return xs,ys,module[:,0:M//2],phase[:,0:M//2] # on retire les frequences negatives


@_odeint45_fft.defjvp
def _odeint45_fft_jvp(f,h0,tol,M, primals, tangents):
    x0, t,T, *P = primals
    delta_x0, _,_, *dP = tangents
    nPdP = len(P)

    def f_aug(x0,delta_x0, t, *P_and_dP):
        P,dP=P_and_dP[:nPdP], P_and_dP[nPdP:]
        primal_dot, tangent_dot = jvp(f.derivative, (x0, t, *P), (delta_x0,
                                                    0., *dP))
        return tangent_dot

    xs,ys,module,phase,xs_dot,ys_dot,dmodule,dphase=odeint45_fft_etendu(f,f_aug,
                                    nPdP, h0,tol,M, x0,delta_x0,t,T, *P, *dP)
    return (xs,ys,module,phase),(xs_dot,ys_dot,dmodule,dphase)


def odeint45_fft_etendu(f,f_aug,nPdP,h0,tol,M,x0,delta_x0,t,T,*P_and_dP):
    P,dP = P_and_dP[:nPdP],P_and_dP[nPdP:]

    xs,delta_xs,ys,delta_ys = odeint45_etendu(f,f_aug,nPdP,h0,tol,x0,delta_x0,
                                        t,T, *P, *dP)
    xfft=np.fft.fft(xs,M)*2/M  # fft avec normalisation
    dxfft=np.fft.fft(delta_xs,M)*2/M
    xfft,dxfft=xfft.at[:,0].divide(2),dxfft.at[:,0].divide(2)
    module,phase=np.abs(xfft),np.angle(xfft)  # amplitude et phase de la fft
    dmodule,dphase=np.abs(dxfft),np.angle(xfft)
    return xs,ys,module[:,0:M//2],phase[:,0:M//2],delta_xs,delta_ys,\
           dmodule[:,0:M//2],dphase[:,0:M//2]


