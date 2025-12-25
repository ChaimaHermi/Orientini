import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { SharedService } from './services/shared.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const sharedService = inject(SharedService);
  const token = sharedService.getToken();

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(req);
};
