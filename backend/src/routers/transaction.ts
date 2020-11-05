import { Router } from "express";
import { CreateTransaction } from "../controllers/transaction";

const transactionRouter = Router()

transactionRouter.post(
    '/',
    CreateTransaction
)

export default transactionRouter
