import { NextFunction, Request, Response } from "express";

export function LogRequest(req: Request, res: Response, _next: NextFunction) {
    console.log(`[${req.method}] @ ${req.hostname}${req.originalUrl}`)
    _next()
}