import { Routes } from '@angular/router';
import { ChatPageComponent } from './modules/chat/pages/chat-page/chat-page.component';
import { LoginPageComponent } from './modules/auth/pages/login/login.component';
import { RegisterPageComponent } from './modules/auth/pages/register/register.component';
import { AuthGuard } from './auth.guard';
import { ForgotPasswordComponent } from './modules/auth/pages/forgot-password/forgot-password.component';
import { ResetPasswordComponent } from './modules/auth/pages/reset-password/reset-password.component';
import { CallbackComponent } from './modules/auth/pages/callback/callback.component';

export const routes: Routes = [
  { 
    path: '', 
    redirectTo: '/c/default', 
    pathMatch: 'full'
  },

  {
    path: 'c/:id', 
    component: ChatPageComponent,
    canActivate: [AuthGuard]
  },

  { 
    path: 'auth/login', 
    component: LoginPageComponent
  },

  { 
    path: 'auth/register', 
    component: RegisterPageComponent 
  },

  { 
    path: 'auth/forgot-password', 
    component: ForgotPasswordComponent 
  },

  { 
   path: 'auth/reset-password', 
   component: ResetPasswordComponent 
  },

  { 
    path: 'auth/callback', 
    component: CallbackComponent },

  {
    path: '**',
    redirectTo: '',
    pathMatch: 'full'
 }

];