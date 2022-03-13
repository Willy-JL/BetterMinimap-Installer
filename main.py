from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import subprocess
import traceback
import tempfile
import pathlib
import struct
import shutil
import base64
import time
import zlib
import sys
import os

self_dir = pathlib.Path(
    sys.executable
    if getattr(sys, "frozen", False) else
    __file__
).parent


class Quit(Exception):
    pass


def ensure_cp2077_path():
    global cp2077_path
    root.status_btn["text"] = "Getting game folder..."

    if cp2077_path is None:
        cp2077_path = filedialog.askdirectory(
            parent=root,
            title='Select your "Cyberpunk 2077" game folder...'
        )

    if cp2077_path == "":
        cp2077_path = None
        raise Quit()

    cp2077_path = pathlib.Path(cp2077_path)

    if not (cp2077_path / "archive/pc/content/basegame_1_engine.archive").is_file():
        cp2077_path = None
        messagebox.showerror(
            "Invalid Folder!",
            "This doesn't look like a game folder, a required game file (archive\\pc\\content\\basegame_1_engine.archive) is missing!\n\n"
            'Make sure you\'re selecting the game *FOLDER*! The one called "Cyberpunk 2077"!'
        )
        raise Quit()


def ensure_dir_exists(path):
    path.mkdir(
        parents=True,
        exist_ok=True
    )


def ensure_temp_dir():
    root.status_btn["text"] = "Preparing..."
    shutil.rmtree(
        self_dir / "Temp",
        ignore_errors=True
    )
    ensure_dir_exists(self_dir / "Temp")


def float_to_bytes(float):
    return struct.pack("<f", float)


def run_proc(*args, **kwargs):
    return subprocess.Popen(
        [
            *args
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs
    )


def proc_log(proc):
    return str(
        proc.stdout.read(),
        encoding="utf-8"
    ).strip()


def wait_proc(proc):
    while proc.poll() is None:
        time.sleep(0.01)
        root.update()


def save_error_log(log):
    with tempfile.TemporaryFile(
        mode="w",
        prefix="BetterMinimap-Error-",
        suffix=".txt",
        delete=False
    ) as f:
        f.write(log)
        temp_files.append(f.name)
        return f.name


def setup_variables():
    root.status_btn["text"] = "Preparing..."

    veh_zooms = {
        "default": 100,
        "slight": 150,
        "medium": 200,
        "big": 250,
        "ultra": 300
    }
    ped_zooms = {
        "default": {
            25: 25,
            35: 35
        },
        "slight": {
            25: 37,
            35: 52
        },
        "medium": {
            25: 50,
            35: 70
        },
        "big": {
            25: 62,
            35: 87
        },
        "ultra": {
            25: 75,
            35: 105
        }
    }

    if root.compass_or_minimap_var.get() == "compass":
        settings["rootWidth"] = float_to_bytes(9000)
        settings["rootHeight"] = float_to_bytes(9000)
        settings["contentWidth"] = float_to_bytes(450)
        settings["contentHeight"] = float_to_bytes(999999)
        settings["borderWidth"] = float_to_bytes(0)
        settings["borderHeight"] = float_to_bytes(0)
        settings["highlightWidth"] = float_to_bytes(450)
        settings["highlightHeight"] = float_to_bytes(450)
        settings["backgroundWidth"] = float_to_bytes(0)
        settings["backgroundHeight"] = float_to_bytes(0)
        settings["marginTop"] = float_to_bytes(0)
        settings["marginRight"] = float_to_bytes(0)
        settings["visionRadiusVehicle"] = float_to_bytes(veh_zooms["default"])
        settings["visionRadiusQuestArea"] = float_to_bytes(ped_zooms["default"][25])
        settings["visionRadiusInterior"] = float_to_bytes(ped_zooms["default"][25])
        settings["visionRadiusExterior"] = float_to_bytes(ped_zooms["default"][35])
    elif root.compass_or_minimap_var.get() == "minimap":
        settings["rootWidth"] = float_to_bytes(450)
        settings["rootHeight"] = float_to_bytes(450)
        settings["contentWidth"] = float_to_bytes(450)
        settings["contentHeight"] = float_to_bytes(450)
        settings["borderWidth"] = float_to_bytes(450)
        settings["borderHeight"] = float_to_bytes(450)
        settings["highlightWidth"] = float_to_bytes(450)
        settings["highlightHeight"] = float_to_bytes(450)
        settings["backgroundWidth"] = float_to_bytes(450)
        settings["backgroundHeight"] = float_to_bytes(450)
        settings["marginTop"] = float_to_bytes(450)
        settings["marginRight"] = float_to_bytes(434)
        settings["visionRadiusVehicle"] = float_to_bytes(veh_zooms[root.veh_zoom_var.get()])
        settings["visionRadiusQuestArea"] = float_to_bytes(ped_zooms[root.ped_zoom_var.get()][25])
        settings["visionRadiusInterior"] = float_to_bytes(ped_zooms[root.ped_zoom_var.get()][25])
        settings["visionRadiusExterior"] = float_to_bytes(ped_zooms[root.ped_zoom_var.get()][35])
        if root.bigger_minimap_var.get():
            settings["rootWidth"] = float_to_bytes(510)
            settings["rootHeight"] = float_to_bytes(510)
            settings["contentWidth"] = float_to_bytes(510)
            settings["contentHeight"] = float_to_bytes(510)
            settings["borderWidth"] = float_to_bytes(510)
            settings["borderHeight"] = float_to_bytes(510)
            settings["highlightWidth"] = float_to_bytes(510)
            settings["highlightHeight"] = float_to_bytes(510)
            settings["backgroundWidth"] = float_to_bytes(510)
            settings["backgroundHeight"] = float_to_bytes(510)
            settings["marginRight"] = float_to_bytes(500)
        if root.transparent_minimap_var.get():
            settings["backgroundWidth"] = float_to_bytes(0)
            settings["backgroundHeight"] = float_to_bytes(0)
        if root.no_minimap_border_var.get():
            settings["borderWidth"] = float_to_bytes(0)
            settings["borderHeight"] = float_to_bytes(0)


def extract_inkwidget():
    root.status_btn["text"] = "Extracting..."

    # 1.5 inkwidgets can't be edited yet, this here is a compressed 1.3 inkwidget
    inkwidget_data = "c-rk<2YeL8_n!+1CDag*E|DVA5(tn`(=G`Kq>(}Z17UNwxvaU|o>zc?B?2NSND&KIK*WL|(nJ)+0HOf_8;YoZ1r!8DK?D^=`M=qj-JQMNGzk8Fzt6{L`0mcWoq6--y*F=WcVEnz;kmn!{%6G9<oD%cL#Ee<^Of-1vH?POrgv_!2{0JWSFH{?II1B+?cn(N%V{sPY=n>rj&nwDKhuRCkG^>1MRYAcf}=QBu-bS}icsL<T&0=3TlBgtJhF&lvEZ;}*f~$3=qf=8W}kwLl-TUV^vu-!3^THmo0C0!i5qb)7gsvew_<z^Ik*xYnbYvUnWE@HPR>%y*?5#y#JPBDJm=x!yoH6l3ytK(65it~Mf@}m?{aW<Qj5UL)w?qJ!l9Ki&pCt=&LfBp^#af%7f0{H*JJfG<Yu|ac;3l7th~blttN`DWCtl`J4q@uE4LPKZa&Wj-E-Qx(mb12$eSwh=gun;aC1%>^KbX^ZcjcOIR!^3a75^8QGwgTb9PVBwN&90T^`PUEj5r{IGmPisl>`p5iI;Q$%40dU4o}HAGC<OmWqnF>72`&Kb3PiK-I5JwnA-gcNU2bKCgs#yTKgtEut4I+cgZywF<&o3Z^Pp^7$#e<C@e|u|#($wL62GEn-QD=*TPK1PAopF1jRQx2M$3S595zg@KY<%`Xz|Rw6FWW9QtJ-{UUgtm4%C0=rn?u8O=+bU<HR+->+56XJqGkchpsQfkpvAb4ERh<s4(eZDf2xXGtyRk2rzuxlVR5P*|+)0W6dzPr?6sfp}x&9d96K~qF&svJqV9~PJB24(~oWlTA*i4bU)2uQ8rBTyqdZ^4R(c!x~@<AN(PZ6Rm37r@kGL@oc|+10P-*!JxK8|E&1q!-}ft@oD>16*>)`mQ4Z{S%vfkqww}?gx_yIH!Z<K@Z@i>HMncfX{9ka~39f)WQA!koy3)KG@^fV}KhYg}qM$KK)_x$<2Um^ICcj1NKPY^UhCzw(n+zwgLuzj%>VP2;hhY$GfJR2w#gReoV2oAHfL}pP+bxVpu(b4vH^O{E1?uKmOMrc_^-;_$kGJ0D=Q37E@eJ@i4`f^$EsNv{PI|@mq?%KeQXD-V}s}HexRLp?au3VF7TZ7ni_K1JqC|ZiE6+V{~a8NC|$;mBd*;)9X(beRxWavwjRh=-k)on-{c12upd<%UuTa?SP;*gznn5{;_*IsBzZAaEx_gh->wUI*qe%6p`$3dpHM#4K9d<$W>ItIjnYGjco9ZX3jB%bJKIXXcH`Ea4RmXvo75YDL&V+&3J`uuSawVoIMui1q2LOig{0RJPpNCiTglaH}AqR7!7XJnsej}aGa^|nhdd#M<^7a5hzdcS`(nr(qu=Wh}^<-9*qTy5?$eF97?o{oCl3ZVqu{hy5LaaKjIkFhO+Rv98KlAz=M#=4a?nZp&Hw1XpyBzuv=ZcgJ~qyYxf9dxm;J^+j(^y#_}$YVBzc;oP)Q^<0VZ!5Xi!<@)%Cl-3&fU^m-U2Am=5V3tW@L0y*-CPBb>wF4&~P1i3*{k_{I@U5Z3WBnh$P5K1!zTakxe$`A#I2f1+I>dJO;4mXa~GlVIk)Ow<wpQd3Prdt<}rU-7K00tsX6zzzE0Nmnn6Bcuect?_8g^@;P9>*lOmgEu$QhcfrTo$On=@MaNJf*3e14vlq%<#ElP*fl|tPpiE3kaDaj$Bcym$cRc9W~=%fha--=P5#|5J8wp0FlXCkq1I~uZxeBW)S9Dq8(NlNg_6nLcx<QVsnAsp#st45lc{#Is!>xHPhj$JO)GvP<2v#CTSeEGt$L_fa2_49>v<7MVzXP*(?W?oea*U$c@h2@~NvxEGh81kq8STh-Z~zQmPD@m6t3m(+eWUTxQ89SsoYfu@n)lr#j`5w8Ji1q%aJT5GW2JAiV0LhoN!c5o|69JFU1^UYGH;bjp@mN7n6L(ENON3CyU7_E$9+e3mZRyt3G0Jd?~4rt;NTe0NT=dg{SPcG3eZM%+`Z5jeg|B=MCZ^F*ag@dB7k@(U=7FA@62fgnj4_ER~aNCU!=o%g`dnjy}RT1Zh(bFjOSj;6Y#pvERSIZTzy7I5HX<$?qU2Nq>j?uhkdh;BjR|2D51yG@JQn^9~@cBvD*qcmvvnvVvSU_Hg<=~H-Dp<SGsA=(8?DT=k?YO_VDN7x-Jx3S*J>j2$NC94egNElP6JU<8}e7xYs!Ikd>;(<#pX^b@E3&I9Nz_S-!6JR=tj4`xWh^eOVl3_5VaiX;p4^l2K^^(|B3SS7f@>aoHf*jZ)9V8%=s>F4t`4;lTQRy6Za)NXLvpdo*fH}zLZh271ost(J6#4yt8eD)|(ryspIO*T<lBAQZqxn+Qx9`xteM4eXC0;;TfLpp;b4wFwD(6h%IXo8>V($We!REDdF08p0yl;Z0@|;t2<V%yE8=N{X8Gv1wE{!_X=M;SrtsIXCh!E<Rj62<BC0;bate#>^g|(}d6*j#cd^`4SM6bZN^RAEqpbjORyO_5!b=$cTC#Z;|v}!SE5<eES58DKo5Ls>GSRyo0u-l0vBn{wmRrg@kBTAe>XpsgrWr42pSyJbz=Sy^9d0@Q*&xV`HcS|k>oI2-GF3>WT4C-)s@-1Xig4H_j#&v6%i<25B>@gzAf(1{Ov=WeRWSEi`pZSG$!I@uRgORrLbS}W%(lk$;5Zf3DrPNl4HZXdQZ_&)?k}Z=;RZ$BTa0+zLB$pMMAyFh-L{c-oLn0(zT4P&w&;jOJIP}S(wLWZ(N~=5_p(J3@F0sjwnql7IJa~qqqm?BVdL&VRGJA@6m&B}%2Q@FS<y%ECMl3VQgMn(sxxDV8Y`FmRqX^ktf;AHxBc`K~P5~z?kK_aJt^qEBWu%jHyBXaiF$ODQDKbg0^H`Gd<V5e2LlTGR@)VIuh<r8iO9YOeXk?S7%*MV}Aq8k|Ihey&Wr5^NCsK@VDUxF%8{NE=%9OJ#CpVQbsS-Sk%QvRt6PweGgBVS-DR2OVc;`{B-02>Jw|Hp0BW=v6x?z=qY6vjMv<qurD?KU%ZA^Bgz+xEgbBWlxas^LO7H=bJNE(S3Ty!0bxsjA4TUsqxrS`mzN*qLiO==(O2CuQTM6ccMw&3_EKf?tQbCs&$L_FszhMs7(y}%|9r0gNEzTsKQaM6=Y#G+g9&^3+1Aw%HS420A#B`}xHu#1+b6|zENg|3D-y1`NBL?h|Z8*#8LIx;z!>D*)aA^|HYTP8Imt<%_2Y4=%x5oQY$rqM#IN1*mtsJ@((sEVsmW0k_G_!pJVmxdaZyucA%cB{NauhCa_smeqM8hXhpv?jv{j#A0X<aqT_fJco{l(n!LLDC{O<C5hW%ixj}K+yTyOm<swAHmyUQ&gSdzk8Mc?p4-$uae!`+L3?L+#B(B+|P4v=n2R@cWTa1zz1F^Ix-6IVZZimCIFV&wjaP-hJTECXTbuz5q0js?nmiX;*)^Zi4Pol7I5bNq`vF%13||T>$`w+e|xC;*MNO?#B@9hIDCEElNSKbMK^ryGTur|^_%lI;GP#M_WJ`vTSoiMsSmhs(9)JoO=QcmrHO1+wgLP#*!e~$!0xLO#|#II?69LK8_;p$WK03z2j^DRF9qCme)#;EfTjLNn=c1^{$l!~wSX(bnti+ru;<HN?mGgQKEjoE6tL-?`*!>Y7&km<>J`BJ;DgWB_d}=?H~Oy|0B=2fCZiKzX}{C99)QDN;NyD(#;s`)9uBy;U6YD<z$doccsvPk>0j&0(*e)MoPG#zeJ0M`H`oHW@10fOh=AiKueHqv?DpOJeU|{<y~vyR6yQy#nuR|H_~hJ>inV}|J?1{J8*ufOUd#3YR&4uq_YuHs%OkVC1I+ak+x-SO?6G?e1l2>R?+=?#b_48s<<|{;0iU|>t<#BsjUy*7%>vB&eB_RafdBVX=Ib^<Z(6^1reJ#UX!BWs_dXW7W*Ok|kyC$o4lpq2gYGW@c3i(Qa|_^rm5X1m0DQP~#rq!uzJ0?J2R{eAqr<wtzru9U4}bD4<|9hjc^dG6V+p&?0&;hkivj*1r{jkX1_7>kvHR{2z*FNdEeQjBF6FMhc&m5z<&I4f0Qby%C2<U3LAwsECjdS@bIb)B;B9~07cBys_gz{!12EvTR=M{8o?N?h`Tc-%+K#*ZVZg~rX*X>I9RK<Gg$DsgY;T-?0`Sm^NjLri`1P{Uf3ymK{&(mZdJ|yRb<M{02b^*5z-BRk>)tpqHU;pmn1|bq0UTWL!=Z72G2f3kX2Ip(@857Y;42wFFPR7U<E$6fJp^dF^0w^>!1)Vyee(>UaDT<>^?+&NO&h!kxOVX`-QNZ5AH09^A;5j}j*d71IC9o~GcN)Dc31h{CiS77ZCl&42fVO4Evz3PKlPTq5rBu?fm_o6x1RkhfCG#RnQ_GdxNuFQpYH=)R95iUa==?w9*Nuzc)HhyV|y?z4xarbVE4q<-+TiY-1g7xGl16qd$Ro+AauoAl+_V%PvldBdjLMNF5|aQz&G0lw2lV!6wkJ11K!K6iOK`~{`XEddjKCTS$=UgVA{;zA9@f_eBjH9Wq_TBp`EJ$UtIlKw{?JLvd;a9UmRGGbMDV=fD>HrE!YJ(W=72M_W)-<v?BBazzrS!SA7DQWB%&GSAeD&TRu7i_{U|>&hvn|@o^9S0r<uSzr=bC;d+z&1<e5$cWVD?Yd~R3@S0ly8(p07>oCC4e>uezK=F>%U2*|0Z2sn%LO|;`6*r53gX%SyJ`=F*h4G(02-tO!f5anzld`PIFW~#4-Vb;Sw{!EmP4@#f`RkGVZvemV(dp?+fKvk^LQo@w;+ytwiC=)Yr|Gi0I|D{H_ZuA!c*Dkx34;Mc6aBX)0!DoGjwK&3w!_k?0-#Vnr_oHnHfRq27~r72XTqKb+;Su!;}yW)hc)X}4tT2k)t~kNPMz{c#HWCdKi0I>DZojmZa&~2h|sc+GQV#R*yG}+<X(X1mW0^D0N?Ji@mvaE`D=F#%L2S`{=;pP08h6nh!g=`bKYt)1Mq(5#CBzXh1TMrMSxk;p7`}~z<|HL>c18+Xu;X}<$#^KhrRg$VCIrRmM;MvV-K7?26(0X(R!x=xu_k7&trblo2;nU80Le1O)44!Zuac>HVClr%Hks(0ox}I2@V0YUHbBs-hdBueEIAEz}rsEiHHZ>``O0@qX8o)`8$dMJ;!fZG9B=SxnjiqfXj1-UtSJ4XkV6jHQ-GvzxZrD;C;zM2krozu{}@N518C`#=#E(-+ZKe+gE_k+`g;RkC=YV>4ZP=`P)Yiwrm3P#Y>&uZUbl^>AunpaCHCZR|Wwd={Yob6yVz<AN(p8aBEoq@FKvK<2)DafUEBu^WrqXPRm!UnF*Lzwq@@^z_S}X4W9-KeKL9BCVbwopxL{CF(06DM*(-A-#XzZz#DIx;_TEEu3y~Scp%`L8((tA0RGvg#pZOt;e8hmD+Uy~^rrIxZ@IYS+zP;qIQyuV0MqX&I=>n4Q|pcg-U8e<{&CAkfZ+X`oddL;IQ(SeX5jw<@5<~9xZHo{l0kqAmo}L;3b232smJpHdkpOR+;l+h!ULb)3m6hUgL?w7(M!D_dkJt$pSy%|z~{aFIvoVOVbu4}oB(Vwt4qM&fMFfBUkYlDP|}F+f_egudADb$Va>^-#CX7WzOaXn1$?+=R7U}D<@Q;*v+?=DY2gn84qlT!U^U>blk1$@nv+LyCn>gXK`@!(REjTCJVmiX5W%q&=TO`bRQ0314mkelu9nM`Mfjha)$#@uo8oIsc~kijA^duo@@5p1;ddHS-j2C%CsTeS#m?}1kSPzLxD7uXG@x&TALaH?%llKrk9^<gVNBoq7PUN5<{!sDO!+YRWia?n=&7gw9mjh;jp?WN($nL3?$ut#^l$gp%YPysqdt26@pw(@W6V!!ALIIO@2i&Q%kl(%)-&aknQ<%()7OJVFEHiPDZUE73&V`%oY+rKe?RUUQ+@|CZr}CO^LYh7g70tKuQuU&`uE{Cn<<}15y$mi2N?4?ae$srOz$zE$MRWkK))2fI#5ad2?O<fVgt+@Xe{TvL3;W*KtFSkF@3{Gz5ZmvZ)l{RAADa~q+WlLq5kcW#&Y%_qOZRUeq)E|>&Gug?lhps>!m|OjOAH8R8NoBPmZC+eq+!uV>!ePGq#taVfy}dfd0-JW?cVM!;R&zcDTMC{Hn;Q;l}*T8=?10SPn0bsKj2P^!2v@J|{*Q^HUP7*Ax6I%8Sv)^p|4va>n);5o_#+%VYKYw1@h?j;*BrI6ZxTppP&c)7#>W=~u@a(|?knr@x3_&P_C?Z!l6%-yG_XA8AaVm87Tdf?q;OGN#{@tfvnH`m@Q#^f!*y(}x26t)q?ga9)aWJ&&a5^$L&U$0?Qgw^V(*N3efO)z^<-nMzI5>j@UY(`m-`emc!~951IC*WWioUq3eWdoqmma641}CB@s}_j9KFYl=4f;`JC~J~xfgw~Oibj4}30eKPg*cn2vg(|EjAWg5%>Wu{zyQ>iP+=bcPrzi~Rtn7(<oF@1QBv40+yW8AOLa*XZbiyY(e`hKih{wu}JKp&Os^GaAlL|z2D0A`7g=^K0a9kGVA?Z&7HYC*~TrE3VahD9WP0qh2lR$GY@pEU<MJo+dIwUi1GI%W=LjuGmJI!R|VIBiJl36%S!uOTpAsiCYHxS3XZl8{}&%rS9#FpboggXWHKLtDx{rfLbl-Qbr7cXDTLLS0Z-MIzl$ca%fMtB0hE=oY1sb2}003Af|BdZRw5uXGfO!t}hAMXS7#pMKR7$x^~E@Qst3AFq(i--YCE$peE0*h1T#a5Ml7ltv2;q6a3qgAHj1rKN`4lL+GhsE7+@j#cIwBOMn_)MbRs#b8CKn8hLBH5yXei<g<gjO1%1ouEnvCcs2AlJci=D$6{{NalzYXEgaInb^%Jdck%7BhjPjaaO?Ys1$nq^zR#^Qkiivln7!Zg5vQ1X%aJjD4q6Na&yDM^+!<2peTAJ8pY6~ShhG$DK=~6H^xwY&3)x3&3APms7yu=|7oFR)tS(;5v%C3(1Lu0CRAeHs4kQ)2aT18bN>U9%&s#@PSE*8$z`Z6&zM7`a(FIQbs52`%V<SsmsZj&qRh&2ySJ*&OJ<-YGnB0<GfDCYcGiyIQM2kTPnxS9%}_?|Tdf}%tsAWK=bR%(Gsp5^&70e>`oRieCcweWVAWFwYf=pcD~~PCREj5RXX`eM0J*9K*p{&cNs_shNHQi?mE_DgRNKi;7VLll?&!L;g4fJi9V<W<GND_m*2nU4{4b9RCAC|e5o=CPOg6`c#3yHEXC|AoZK#O8C@)Y^-iC^iUAh}@ZIwWbRA1VzazaSk5m)Ator+s&B?%%G5AsTsQ_xiSj~q>d|L{>M<qMB{XE{!(#7NaaouL`astn*5V*p1O1DIkMx72FhZ%=~~iToi|(HTXFiP41y9VA86sB1^2XG@fxwWB?YVnY*^*;$6Z7x~U(GP5_a5!6Gz4Bm<EB3JIFjdzlY@AWP2EUUB3ZkgV?IxyCCqfs9sYTE~$z3}b2M9KCt@1y6UWqY~D|CQ)!?WMwJ*1#5k!?3yi`wtBt5R#FqSNz!;#joB=-NP0OO7Tps?B-}hW*CKD-=5!x=1P&OiFRxeWo)q|lK`^DtX3BH%SQhIrI?Qv&}I(oPZ{x`(&Rw%LXD%+m_;X5yJYz+)$3L}pU6zs?yksJF(1~=*Tt21h?P6XYs|Z94^bm$FSFHMzcRR4YFoqVBl>=JV{E90k#h8|^I*!zEO3+aL(|gC*<ooRnc+i2WOWEo)ZtM@9a?DSgvV$p?lYbrT4?5nt8n?t429E^bub2lTNcd>?k?lOz21_nZk-#=%-PF*X_qf+r_kbKeC=`cgtB=fErU};%V@r|Yj}A7$o@Lh{SS=QlN#fz!EVS?XayqQ(aEOMTQ!}5bdBAIPSN4CLA>>dw*k|o)gcM?aeQd^H7}W&UX0@O^<4vL-Giz%Av@JYxN~RK5%j9++(Vh~+A{k3u869N1w(c+wB_Um5|Y<fLh@&>e*N^cb`(}?Mga?aAiI95;i}xA%exs>+RbdNg{cZ8&vE^<EIq5R6iQhdUB%|h_2aa^Zt{9g*-ae4ObV>}4x}94QVGXSW`**Ck%xQpjW?7);`d*tD1ii4t?JaQtdY7EDYYc`gg)ex_Z%D4z;isWUkOJ@{Z#gGWudH5gc8XJC7cn;U@DaS%62PbuW>u02IhM$a@D!T7i9;fx6HMMg08|$pRbXbu0t=;qZEBq!peH+_1bvTcXfTGYE)@AUe@reH|_D7EiTniYUI9au|yoM4**BV9aXvApl~~kk#Ll+ge6B_tIf;h%a%pet%mweFp7q5u6iMiO-~-#hRVopL9bAS*;)e)-e^4Zo3z4w)lir*hKm4|*U1d8A=m0AD%mwgQp}<rr!dD?AD+|LZ(zTO{t;De+4Qa?xRbYJBGBvbpS<ui9t&O(`ZnVg?rYky*nYhx{fbz|-eQg7$2isU<R@NcX@*2-Bz?DwVe}1!(O5=l;;)yFt6Q5q7hA~&;PR{Uw>xTJi*MG*4Zme5*2Joxc|BCOk00vV5Ls!5#QihUF0YZacN$7Nsm9VS|5w_zkoGQpe8h@<RMlcvgVII2>hyW#f&D4hGUe+f_I3><w!20W+he$rNihuCnYGtj*Z+C$ptBXqn)|N#rOKK+?ZYuqbs4n3TLW3XQzKbcRPjy&E8R3-HH@lk3i~g3eW0q{iWr9WXpFIO@2#`lihYKvno;$hk?KlU#;W!`xtcwrt+mtNz{6dKU*A!95ABy2J76H;gXn$c=|tVg`U9gSr@Yk9tYrTqtA;~iGVhRG$y49Ct9bzaVRetA%KpK3XjGwp#4hz4)tTHs)&=L4ZK9vr$!>?To9I{h<TOXWEFLR8pVTmTNMSIW8Tnk6+5Zwp7SHrE-f#>*m4_{rZgSOf*z~VFe4-WBVU4h=*|V!)b|1&<_em#ctNu)>dK@zjx7IYknOx0s`pAD|>S5!`*xEjT(U0%v*L!@w&{?bI{iChSQ^$$=rSByAn!QEZ63|rqe@ex9Mr-t1PETUXSwr>G`HF4usII{v?WTa?fcb92$(_X?{~Sl(s4vg5ip*)ddQ53K{~B7>?==+YHt@eyCNL{Af#p>;ay2kleXG27vpvw)qZZ1a!l`VXR9LYvmTdF2<nGmPa~Rm;<2f%Y_V{d{ZxnlMmi~VA_E;7Zta;kfubTHl7$a<~sM#rWnhC+aS07Qt{-C~(6n93BF@97;TK!{+@3eya$xx8Ozk;l-AkS9qeXf3ourhy9th3c~h5=^DKf5elzHGeyS<>;Nla==^@v*E3uWj2lqAr)Eztmvz`ngt<*Ll*#-_Y;mMTJY~59xjQdeX}QUm%=P<WF>2`*K;KbkASD#l(mGttw>P6?X5}q#m1;<0f&>B0rO+8uIY>tZ(sc^b=ZtZSf@Xf}W|qwwS!<(7?BteB9E|)JR)Qrk_AlV{I|{-mQs=h^ncnnaPKz4)n7YpO^1$pkLMbG)}%44f3TX&zM^JQj=E?gMEvc&$#4F$W5e7$ai)`$lI~<Ovqk({i9PEM`Rz+1wW6Rl9YiHMR@T@58JW%w#MXxnWHxk%3ab}&4j$FF?or({%gkuqHFoN>P*NqbC6e%GeXgF=8sC~b5i|78HTG)$5@w1h&9Qev-uLIo%8T+Z3^Ey%0?_Dxg@!pabjYhq|W1g^1Vt)B~y4C@37WYiq_hvTg9V;GeuFJfO(uS@gK}eT)?E9WbzWT8SW&e2!)!%SkCyXr<Bv-Rgslg%9~irywOS~V>WNJlx0g*cv;_ZsaZ*puUwa?$scopE1bgygICP+&SXa%&P3;?!jL;)2ZPKm5-i0I-tESj3C*;h5?cw(dDfVm*vtep1-ijcOA*{2DtuY_%;FSnmcd-|2Ro|C$}FeL%f-oxHG*cZ&~%}dU1oA1JNdDkOW+(Hl7yKpz)1^Z9afTn6v@f^^bNCD3>s!H%MJS^;Eu-{F8jSuwH{4kYntIwlMlQ49Mx8++6`vR2>@;anIdP^@`y_eSjWXO%OrQ2>a2YJLXa+%@U>>$t6fUG>-2{tt~!Svlf9wR^l_8gP5u#Yx#IL~c%u!ciNo6ohup>SI4ucI<A!H+oW>2OjlgN#)*+I{?R7-bxP6F7+9v$DGfvy|10rdgaQZl$-t8|$(z~^$>D_Lo>D@+{Ncy@|z`1!}9?3P4v}*Y#l2*-1)4knJ)4k22>E7-)k#ui3T^vsL_Oywld&6nta9XMjCX%LZtBIt4d)-9R*}Y{V>FnM$k#u%@X&SrtOeEbHPBXW#*P~rem`FOY?@c6~*v}@CPVBOYq!VlFN79LP@gwQP`uLGFVMF{#ny^uRBu&^Pzze5x9VIwD-48$SchfX*vuGN)C;dnoxD9?J4cu#fBn{k0ek2Xt*MNl!nk@LikEDUS2<Yr}&ks#$dbl?ANIJI8fPe4#^SvQ7{aXx8|CSB7=!AFs_<AJ$-Q;>C{hg~GNq>ja$>H>Och)26@8;5Uaf|Db^mk7JMxE(1bS+?~0k4+4httmea^Tia07K`$)c9+_f_p#ja|W>6(%4)709?3h>*a<xZQFM1rdEKvhP?l1H^6rS-JkUa49m*AHv;hEappJU0n6rbn??a<dS;KC=ugtr75bAjb+`GGG<8mYlBUk<Ptw%kbaD-BP4njh-mvIm<nw?_ojF_u;Hyt|O#B3J_=^`ioCJJtKw;zsz#lKi9Wy~VTE6sr?+~2kEnvdY*Z`8IF9UGz$@!CW02et5ZAAejt)4f4r1QHYfTZ2S>Em#EycGc?J>FWt^$Q2j-3S=Apn1+V!1Q{r-T4;apP8j+-v(U1aL<ol;Cf?n&tCwXdvV^Q{tz~E9c*(u(KK(}=wCF+q*zv;*zI<Tr>pskC-{@t<xTaU)vw0yP%`C#%;*29&D8RiOxl47OnECNElr65J$~W#SEjr>lMbbObM~`untlctKEsp`WIo$34ARqY2m058^z`_JI&ZL^{wJJHGT6BOm935GFSItMKi)<yw^9ti=|S4+>G2mH!`kWTaoS9-oiY8y_IiF^!D(LF8~1l`$4b%{(67qs({)@UC3!(pSbxi@34)|jf9X9ix0H@TdV$mfYjyckVdgYYd)iEU+C+QWLVMa$dn&7tluAL#O3(sSP2RB$(DtFVlvqJ3Y)k9#qkEpc<PU8+lN=G9l`q;tl;hb_egK@#KqBfYUnpx7-%TOHyQ_NXP-DZq-9ly3fMOu?fqx6y$yQpvZ&uh1sFK~#H@6Q`*+n~z*+ms`D!cd@VGrO5zcs#24&*{`fELKclYuyZa|e<rD-cIb@*b5R>P@-CdsU%i$ik?YO`2}>*K`BtQIL}{;4T$cG6H4H2$T)N+e6V(Z80bom?z&>$D;)42ydb3x{IQj?naZ%DRRDW*Tv!0$Ok`XOhU=@+u~8QC!<k{+{08#dSL(ls5F()=ya4p6AfgdEaZ_rC&LzE*s5ZHs^+bd3M<G9i-S;vx(gRcnIDXX(4(Pj@i61!;Y#rctx{$ij%H&znz@yX=CfvbG`}_Bt;Sl8+%PnjY-;Ax3xE7REqWY1{`AnHsPXi8Uqw>X1ZFs@H3W8`{h5IteDy7+F<#`qMjey~{rYjwG1ihC?YQ4+IPOj9xaZ5`9;_YrFXQUea+fb_7p2pMUF9*#$iQes%OmsQ`{~iu>cW0TlKU$$`bp5e`qEQE#ry|fJrk*FU!ql2K{5Xeo+Hm#gYt|$$3(3LafTYyyc!M4GuNpG1s;B8#J?K!pVOcMV+|@W)*y>kgLp#?3X+~aQ?X)I;*2Muvh(H;4Y#sd6)9>}bd}Q)9v6A+emQ?$nH*-#^s8QhVq(?$@k@yUx{ZEvTTJ_Hmj$al64gtvP%EkuLs11&W2;O;m;XB@<YXk|j5U&wqxKRK4JFjN>aeuzh$5kizwdtQ`cH0;FJB%d%WdO^eu`Ik?%D3qR~_ioBBDkA6CsS#*nQltY)&+jl87{xlmoAH$=_`yi(CAF5--`v<4XMOy9<qM@O@-4*Ah&p6<tWSm7YfbKdRU%Dg"
    decoded = base64.b85decode(inkwidget_data.encode("utf-8"))
    decompressed = zlib.decompress(decoded)
    ensure_dir_exists(self_dir / "Temp/base/gameplay/gui/widgets/minimap")
    with open(self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget", "wb") as f:
        f.write(decompressed)
    extract_log = ""

    # try:
    #     extract_proc = run_proc(
    #         self_dir / "WolvenKit.CLI/WolvenKit.CLI.exe", "unbundle",
    #         "--path", cp2077_path / "archive/pc/content/basegame_1_engine.archive",
    #         "--outpath", self_dir / "Temp",
    #         "--hash", "7622623606735548588",  # base\gameplay\gui\widgets\minimap\minimap.inkwidget
    #         creationflags=subprocess.CREATE_NO_WINDOW
    #     )
    #     wait_proc(extract_proc)
    #     extract_log = proc_log(extract_proc)
    # except OSError as exc:
    #     error = str(exc).lower()
    #     if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
    #         messagebox.showerror(
    #             "Extract error!",
    #             "WolvenKit.CLI executable is missing or corrupted!\n\n"
    #             "Make sure your antivirus didn't mess with it..."
    #         )
    #         raise Quit()
    #     else:
    #         raise

    # if "Microsoft.NETCore.App" in extract_log:
    #     if messagebox.showerror(
    #         "Extract error!",
    #         "WolvenKit.CLI requires the .NET runtime and it is missing, install it and try again!\n\n"
    #         "Click Ok to install it now...",
    #         type="okcancel"
    #     ) == "ok":
    #         try:
    #             root.status_btn["text"] = "Installing .NET runtime..."
    #             dotnet_proc = run_proc(self_dir / "dotnet-runtime.exe", "/silent")
    #             wait_proc(dotnet_proc)
    #             root.after(200, install)
    #         except OSError as exc:
    #             error = str(exc).lower()
    #             if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
    #                 messagebox.showerror(
    #                     "Extract error!",
    #                     ".NET executable is missing or corrupted!\n\n"
    #                     "Make sure your antivirus didn't mess with it..."
    #                 )
    #                 raise Quit()
    #             else:
    #                 raise
    #     raise Quit()

    if not (self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget").is_file():
        if extract_log:
            error_file = save_error_log(extract_log)
            messagebox.showerror(
                "Extract error!",
                "Something went wrong extracting the minimap file!\n\n"
                "Click Ok to view the error log..."
            )
            run_proc("notepad.exe", error_file)
        else:
            messagebox.showerror(
                "Extract error!",
                "Something went wrong extracting the minimap file and the installer couldn't catch the error log!\n\n"
                "Please report this on NexusMods..."
            )
        raise Quit()


def replace_inkwidget_values():
    root.status_btn["text"] = "Editing inkwidget..."

    with open(self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget", "rb") as f:
        data = f.read()

    strings_start = data.find(b"minimapFrame")
    strings_start = data.rfind(b"\x00\x00", 0, strings_start) + 2
    strings_end = data.find(b"\x00\x00", strings_start) - 1

    strings = {}
    string_index = 1
    offset = strings_start
    while offset < strings_end:
        offset_end = data.find(b"\x00", offset)
        string = str(data[offset:offset_end], encoding="utf-8")
        strings[string] = string_index
        offset = offset_end + 1
        string_index += 1

    def String(string):
        return struct.pack("<H", strings[string])

    def Type(type):
        return String(type)

    def Size(size):
        return struct.pack("<I", size)

    class Search():
        pass

    class Skip():
        def __init__(self, count):
            self.count = count

    class Value():
        def __init__(self, setting):
            self.setting = setting

    def CName(name):
        return [
            String("name"),
            Type("CName"),
            Size(6),
            String(name)
        ]

    def Vector2(name):
        return [
            String(name),
            Type("Vector2"),
            Size(31),
            Skip(1)
        ]

    def InkMargin(name):
        return [
            String(name),
            Type("inkMargin"),
            Size(31),
            Skip(1)
        ]

    def Float(name):
        return [
            String(name),
            Type("Float"),
            Size(8)
        ]

    patterns = [
        [
            *CName("Root"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("rootWidth"),
            *Float("Y"),
            Value("rootHeight")
        ],
        [
            *CName("MiniMapContainer"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("contentWidth"),
            *Float("Y"),
            Value("contentHeight")
        ],
        [
            *CName("border"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("borderWidth"),
            *Float("Y"),
            Value("borderHeight")
        ],
        [
            *CName("borderHighlight"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("highlightWidth"),
            *Float("Y"),
            Value("highlightHeight")
        ],
        [
            *CName("bgColorFiller"),
            Search(),
            *Vector2("size"),
            *Float("X"),
            Value("backgroundWidth"),
            *Float("Y"),
            Value("backgroundHeight")
        ],
        [
            *(CName("timeAndSMS") if "timeAndSMS" in strings else CName("unredMessagesGroup")),
            Search(),
            *InkMargin("margin"),
            *Float("top"),
            Value("marginTop"),
            *Float("right"),
            Value("marginRight")
        ],
        [
            *Float("visionRadiusVehicle"),
            Value("visionRadiusVehicle")
        ],
        [
            *Float("visionRadiusQuestArea"),
            Value("visionRadiusQuestArea")
        ],
        [
            *Float("visionRadiusInterior"),
            Value("visionRadiusInterior")
        ],
        [
            *Float("visionRadiusExterior"),
            Value("visionRadiusExterior")
        ]
    ]

    for pattern in patterns:
        search = b""
        offset = 0
        for instruction in pattern:
            if isinstance(instruction, Search):
                offset = data.find(search, offset) + len(search)
                search = b""
            elif isinstance(instruction, Skip):
                offset = data.find(search, offset) + len(search)
                search = b""
                offset += instruction.count
            elif isinstance(instruction, Value):
                offset = data.find(search, offset) + len(search)
                search = b""
                value = settings[instruction.setting]
                length = len(value)
                data = data[:offset] + value + data[offset + length:]
                offset += length
            else:
                search += instruction

    with open(self_dir / "Temp/base/gameplay/gui/widgets/minimap/minimap.inkwidget", "wb") as f:
        f.write(data)


def pack_archive():
    root.status_btn["text"] = "Packing..."

    try:
        pack_proc = run_proc(
            self_dir / "WolvenKit.CLI/WolvenKit.CLI.exe", "pack",
            "--path", self_dir / "Temp",
            "--outpath", self_dir / "Temp",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        wait_proc(pack_proc)
        pack_log = proc_log(pack_proc)
    except OSError as exc:
        error = str(exc).lower()
        if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
            messagebox.showerror(
                "Packing error!",
                "WolvenKit.CLI executable is missing or corrupted!\n\n"
                "Make sure your antivirus didn't mess with it..."
            )
            raise Quit()
        else:
            raise

    if "Microsoft.NETCore.App" in pack_log:
        if messagebox.showerror(
            "Packing error!",
            "WolvenKit.CLI requires the .NET runtime and it is missing, install it and try again!\n\n"
            "Click Ok to install it now...",
            type="okcancel"
        ) == "ok":
            try:
                root.status_btn["text"] = "Installing .NET runtime..."
                dotnet_proc = run_proc(self_dir / "dotnet-runtime.exe", "/silent")
                wait_proc(dotnet_proc)
                root.after(200, install)
            except OSError as exc:
                error = str(exc).lower()
                if "not a valid win32 application" in error or "cannot find the file specified" in error or "no such file" in error:
                    messagebox.showerror(
                        "Packing error!",
                        ".NET executable is missing or corrupted!\n\n"
                        "Make sure your antivirus didn't mess with it..."
                    )
                    raise Quit()
                else:
                    raise
        raise Quit()

    if not (self_dir / "Temp/Temp.archive").is_file():
        if pack_log:
            error_file = save_error_log(pack_log)
            messagebox.showerror(
                "Packing error!",
                "Something went wrong packing the mod archive!\n\n"
                "Click Ok to view the error log..."
            )
            run_proc("notepad.exe", error_file)
        else:
            messagebox.showerror(
                "Packing error!",
                "Something went wrong packing the mod archive and the installer couldn't catch the error log!\n\n"
                "Please report this on NexusMods..."
            )
        raise Quit()


def move_to_game_dir():
    root.status_btn["text"] = "Moving to game folder..."

    ensure_dir_exists(cp2077_path / "archive/pc/mod")
    for file in (cp2077_path / "archive/pc/mod").glob("WillyJL_BetterMinimap*.archive"):
        try:
            file.unlink()
        except Exception:
            pass
    shutil.move(
        self_dir / "Temp/Temp.archive",
        cp2077_path / "archive/pc/mod/WillyJL_BetterMinimap_User.archive",
    )


def install():
    root.status_btn = root.install_btn
    update_disabled_buttons(disable_all=True)
    try:
        ensure_cp2077_path()
        ensure_temp_dir()
        setup_variables()
        extract_inkwidget()
        replace_inkwidget_values()
        pack_archive()
        move_to_game_dir()
    except Exception as exc:
        if not isinstance(exc, Quit):
            error_log = "".join(traceback.format_exception(*sys.exc_info()))
            error_file = save_error_log(error_log)
            messagebox.showerror(
                "Error!",
                "Something went wrong!\n\n"
                "Click Ok to view the error log..."
            )
            run_proc("notepad.exe", error_file)
        return
    finally:
        root.status_btn["text"] = "Install!"
        update_disabled_buttons()
    messagebox.showinfo(
        "Success!",
        "Successfully installed BetterMinimap!"
    )


def uninstall():
    root.status_btn = root.uninstall_btn
    update_disabled_buttons(disable_all=True)
    try:
        ensure_cp2077_path()
        root.status_btn["text"] = "Preparing..."
        ensure_dir_exists(cp2077_path / "archive/pc/mod")
        ensure_dir_exists(cp2077_path / "engine/config/platform/pc")
        root.status_btn["text"] = "Removing mod..."
        for file in (cp2077_path / "archive/pc/mod").glob("WillyJL_BetterMinimap*.archive"):
            try:
                file.unlink()
            except Exception:
                pass
        root.status_btn["text"] = "Removing distancefix..."
        for file in (cp2077_path / "engine/config/platform/pc").glob("WillyJL_BetterMinimap*.ini"):
            try:
                file.unlink()
            except Exception:
                pass
    except Exception:
        return
    finally:
        root.status_btn["text"] = "Uninstall :("
        update_disabled_buttons()
    messagebox.showinfo(
        "Uninstalled!",
        'The mod *should* be gone, if it isn\'t then delete the file yourself at "Cyberpunk 2077\\archive\\pc\\mod"'
    )


def update_disabled_buttons(disable_all=False):
    if disable_all:
        root.compass_radio["state"] = "disabled"
        root.minimap_radio["state"] = "disabled"
        root.bigger_minimap_check["state"] = "disabled"
        root.transparent_minimap_check["state"] = "disabled"
        root.no_minimap_border_check["state"] = "disabled"
        root.veh_slight_zoom_radio["state"] = "disabled"
        root.veh_medium_zoom_radio["state"] = "disabled"
        root.veh_big_zoom_radio["state"] = "disabled"
        root.veh_ultra_zoom_radio["state"] = "disabled"
        root.ped_slight_zoom_radio["state"] = "disabled"
        root.ped_medium_zoom_radio["state"] = "disabled"
        root.ped_big_zoom_radio["state"] = "disabled"
        root.ped_ultra_zoom_radio["state"] = "disabled"
        root.install_btn["state"] = "disabled"
        root.uninstall_btn["state"] = "disabled"
    elif root.compass_or_minimap_var.get() == "minimap":
        root.compass_radio["state"] = "normal"
        root.minimap_radio["state"] = "normal"
        root.bigger_minimap_check["state"] = "normal"
        root.transparent_minimap_check["state"] = "normal"
        root.no_minimap_border_check["state"] = "normal"
        root.veh_slight_zoom_radio["state"] = "normal"
        root.veh_medium_zoom_radio["state"] = "normal"
        root.veh_big_zoom_radio["state"] = "normal"
        root.veh_ultra_zoom_radio["state"] = "normal"
        root.ped_slight_zoom_radio["state"] = "normal"
        root.ped_medium_zoom_radio["state"] = "normal"
        root.ped_big_zoom_radio["state"] = "normal"
        root.ped_ultra_zoom_radio["state"] = "normal"
        root.install_btn["state"] = "normal"
        root.uninstall_btn["state"] = "normal"
    elif root.compass_or_minimap_var.get() == "compass":
        root.compass_radio["state"] = "normal"
        root.minimap_radio["state"] = "normal"
        root.bigger_minimap_check["state"] = "disabled"
        root.transparent_minimap_check["state"] = "disabled"
        root.no_minimap_border_check["state"] = "disabled"
        root.veh_slight_zoom_radio["state"] = "disabled"
        root.veh_medium_zoom_radio["state"] = "disabled"
        root.veh_big_zoom_radio["state"] = "disabled"
        root.veh_ultra_zoom_radio["state"] = "disabled"
        root.ped_slight_zoom_radio["state"] = "disabled"
        root.ped_medium_zoom_radio["state"] = "disabled"
        root.ped_big_zoom_radio["state"] = "disabled"
        root.ped_ultra_zoom_radio["state"] = "disabled"
        root.install_btn["state"] = "normal"
        root.uninstall_btn["state"] = "normal"
    else:
        root.compass_radio["state"] = "normal"
        root.minimap_radio["state"] = "normal"
        root.bigger_minimap_check["state"] = "disabled"
        root.transparent_minimap_check["state"] = "disabled"
        root.no_minimap_border_check["state"] = "disabled"
        root.veh_slight_zoom_radio["state"] = "disabled"
        root.veh_medium_zoom_radio["state"] = "disabled"
        root.veh_big_zoom_radio["state"] = "disabled"
        root.veh_ultra_zoom_radio["state"] = "disabled"
        root.ped_slight_zoom_radio["state"] = "disabled"
        root.ped_medium_zoom_radio["state"] = "disabled"
        root.ped_big_zoom_radio["state"] = "disabled"
        root.ped_ultra_zoom_radio["state"] = "disabled"
        root.install_btn["state"] = "disabled"
        root.uninstall_btn["state"] = "normal"


def setup_gui():
    # Padding
    padding = ttk.Label(
        root,
        image=empty,
        width=0
    )
    padding.grid(
        row=0,
        column=0
    )
    # Compass or minimap
    root.compass_or_minimap_var = tk.StringVar()
    root.compass_radio = ttk.Radiobutton(
        root,
        text="Compass Only",
        variable=root.compass_or_minimap_var,
        value="compass",
        command=update_disabled_buttons,
        takefocus=False
    )
    root.compass_radio.grid(
        column=0,
        row=1,
        padx=10,
        pady=5
    )
    root.minimap_radio = ttk.Radiobutton(
        root,
        text="Minimap",
        variable=root.compass_or_minimap_var,
        value="minimap",
        command=update_disabled_buttons,
        takefocus=False
    )
    root.minimap_radio.grid(
        column=1,
        row=1,
        padx=10,
        pady=5
    )
    # Bigger minimap
    root.bigger_minimap_var = tk.BooleanVar()
    root.bigger_minimap_check = ttk.Checkbutton(
        root,
        text="Bigger Minimap + Remove Compass",
        variable=root.bigger_minimap_var,
        onvalue=True,
        offvalue=False,
        state="disabled",
        takefocus=False
    )
    root.bigger_minimap_check.grid(
        column=0,
        columnspan=2,
        row=2,
        padx=10,
        pady=5
    )
    # Transparent minimap
    root.transparent_minimap_var = tk.BooleanVar()
    root.transparent_minimap_check = ttk.Checkbutton(
        root,
        text="Transparent Minimap",
        variable=root.transparent_minimap_var,
        onvalue=True,
        offvalue=False,
        state="disabled",
        takefocus=False
    )
    root.transparent_minimap_check.grid(
        column=0,
        columnspan=2,
        row=3,
        padx=10,
        pady=5
    )
    # No minimap border
    root.no_minimap_border_var = tk.BooleanVar()
    root.no_minimap_border_check = ttk.Checkbutton(
        root,
        text="No  Minimap  Border",
        variable=root.no_minimap_border_var,
        onvalue=True,
        offvalue=False,
        state="disabled",
        takefocus=False
    )
    root.no_minimap_border_check.grid(
        column=0,
        columnspan=2,
        row=4,
        padx=10,
        pady=5
    )
    # Vehicle zoom
    root.veh_zoom_var = tk.StringVar(None, "default")
    root.veh_slight_zoom_radio = ttk.Radiobutton(
        root,
        text="Slight Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="slight",
        state="disabled",
        takefocus=False
    )
    root.veh_slight_zoom_radio.grid(
        column=2,
        row=1,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.veh_medium_zoom_radio = ttk.Radiobutton(
        root,
        text="Medium Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="medium",
        state="disabled",
        takefocus=False
    )
    root.veh_medium_zoom_radio.grid(
        column=2,
        row=2,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.veh_big_zoom_radio = ttk.Radiobutton(
        root,
        text="Big Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="big",
        state="disabled",
        takefocus=False
    )
    root.veh_big_zoom_radio.grid(
        column=2,
        row=3,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.veh_ultra_zoom_radio = ttk.Radiobutton(
        root,
        text="Ultra Veh Zoom Out",
        variable=root.veh_zoom_var,
        value="ultra",
        state="disabled",
        takefocus=False
    )
    root.veh_ultra_zoom_radio.grid(
        column=2,
        row=4,
        padx=10,
        pady=5,
        sticky="w"
    )
    # Ped zoom
    root.ped_zoom_var = tk.StringVar(None, "default")
    root.ped_slight_zoom_radio = ttk.Radiobutton(
        root,
        text="Slight On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="slight",
        state="disabled",
        takefocus=False
    )
    root.ped_slight_zoom_radio.grid(
        column=3,
        row=1,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.ped_medium_zoom_radio = ttk.Radiobutton(
        root,
        text="Medium On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="medium",
        state="disabled",
        takefocus=False
    )
    root.ped_medium_zoom_radio.grid(
        column=3,
        row=2,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.ped_big_zoom_radio = ttk.Radiobutton(
        root,
        text="Big On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="big",
        state="disabled",
        takefocus=False
    )
    root.ped_big_zoom_radio.grid(
        column=3,
        row=3,
        padx=10,
        pady=5,
        sticky="w"
    )
    root.ped_ultra_zoom_radio = ttk.Radiobutton(
        root,
        text="Ultra On-Foot Zoom Out",
        variable=root.ped_zoom_var,
        value="ultra",
        state="disabled",
        takefocus=False
    )
    root.ped_ultra_zoom_radio.grid(
        column=3,
        row=4,
        padx=10,
        pady=5,
        sticky="w"
    )
    # Install button
    root.install_btn = ttk.Button(
        root,
        text="Install!",
        command=install,
        state="disabled",
        takefocus=False
    )
    root.install_btn.grid(
        column=0,
        columnspan=3,
        row=5,
        padx=10,
        pady=10,
        ipady=6,
        sticky="nesw"
    )
    # Uninstall button
    root.uninstall_btn = ttk.Button(
        root,
        text="Uninstall :(",
        command=uninstall,
        takefocus=False
    )
    root.uninstall_btn.grid(
        column=3,
        row=5,
        padx=10,
        pady=10,
        ipady=6,
        sticky="nesw"
    )
    # Setup UI
    root.resizable(False, False)
    style = ttk.Style(root)
    style.theme_use("kewlthem")
    style.configure("TButton", width=0)
    root.configure(bg=style.lookup("TLabel", "background"))
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    root.geometry("+%d+%d" % (x, y))


def delete_temp_files(*_):
    for file in temp_files:
        try:
            os.unlink(file)
        except Exception:
            pass


if __name__ == "__main__":
    cp2077_path = None
    settings = {}
    temp_files = []
    root = tk.Tk()
    root.title("BetterMinimap Installer")
    root.tk.eval(
        """
    set base_theme_dir TclTheme/
    package ifneeded ttk::theme::kewlthem 1.0 \
        [list source [file join $base_theme_dir kewlthem.tcl]]
    """
    )
    empty = tk.PhotoImage(height=2, width=2)
    setup_gui()
    root.install_btn.bind('<Destroy>', delete_temp_files)
    root.mainloop()
