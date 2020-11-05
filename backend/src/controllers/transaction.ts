import { NextFunction, Request, Response } from "express";

export function CreateTransaction(req: Request, res: Response, next: NextFunction) {
    return res.status(201).json({ status: 'ok', ...req.body })
}