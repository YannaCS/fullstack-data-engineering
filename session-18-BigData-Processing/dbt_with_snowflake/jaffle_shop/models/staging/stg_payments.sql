SELECT
    id AS payment_id,
    orderid AS order_id,
    paymentmethod AS payment_method,
    status,
    -- amount 在原始数据中是以分为单位，转换成美元
    amount / 100.0 AS amount
FROM {{ source('stripe', 'payment') }}