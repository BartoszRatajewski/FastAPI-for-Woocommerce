GET_ORDER_IDS = """
SELECT DISTINCT
    ship.order_id AS post_id
FROM wp_woocommerce_order_items ship
JOIN wp_woocommerce_order_itemmeta wim_delivery
    ON wim_delivery.order_item_id = ship.order_item_id
    AND wim_delivery.meta_key = '_delivery_date'
WHERE
    ship.order_item_type = 'shipping'

    /* DATE FILTER */
    AND wim_delivery.meta_value BETWEEN :date_from AND :date_to

    /* SHIPPING FILTER */
    AND (
        /* 1️⃣ ALL */
        :shipping_filter = 'Wszystkie zamówienia'

        /* 2️⃣ DELIVERY */
        OR (
            :shipping_filter = 'Dostawa'
            AND ship.order_item_name NOT LIKE 'Odbiór%'
        )

        /* 3️⃣ PICKUP – EXACT STRING */
        OR ship.order_item_name = :shipping_filter
    );
"""

GET_ORDER_ITEMS = """
SELECT
    woi.order_item_id,
    woi.order_id,
    woi.order_item_name AS product_name,

    MAX(CASE WHEN wim.meta_key = '_qty'
        THEN wim.meta_value END) AS quantity,

    MAX(CASE WHEN wim.meta_key = 'pa_topper'
        THEN wim.meta_value END) AS pa_topper,

    MAX(CASE WHEN wim.meta_key = 'pa_swieczka-nr-1'
        THEN wim.meta_value END) AS pa_swieczka_nr_1,

    MAX(CASE WHEN wim.meta_key = 'pa_swieczka-nr-2'
        THEN wim.meta_value END) AS pa_swieczka_nr_2,

    MAX(CASE WHEN wim.meta_key = 'warstwa-1-najnizsza-warstwa'
        THEN wim.meta_value END) AS warstwa_1,

    MAX(CASE WHEN wim.meta_key = 'warstwa-2-srodkowa'
        THEN wim.meta_value END) AS warstwa_2,

    MAX(CASE WHEN wim.meta_key = 'warstwa-3-srodkowa'
        THEN wim.meta_value END) AS warstwa_3,

    MAX(CASE WHEN wim.meta_key = 'warstwa-4-zewnetrzna-warstwa'
        THEN wim.meta_value END) AS warstwa_4,

    MAX(CASE WHEN wim.meta_key = 'dekoracja'
        THEN wim.meta_value END) AS dekoracja,

    MAX(CASE WHEN wim.meta_key = 'smak'
        THEN wim.meta_value END) AS smak

FROM wp_woocommerce_order_items woi
JOIN wp_woocommerce_order_itemmeta wim
    ON wim.order_item_id = woi.order_item_id

WHERE
    woi.order_id = :order_id
    AND woi.order_item_type = 'line_item'
    AND wim.meta_key IN (
        '_qty',
        'pa_topper',
        'pa_swieczka-nr-1',
        'pa_swieczka-nr-2',
        'warstwa-1-najnizsza-warstwa',
        'warstwa-2-srodkowa',
        'warstwa-3-srodkowa',
        'warstwa-4-zewnetrzna-warstwa',
        'dekoracja',
        'smak'
    )

GROUP BY
    woi.order_item_id;
"""


GET_SHIPMENT_DETAILS = """
SELECT
    CASE
        WHEN ship.order_item_name LIKE '%odbiór%'
            THEN ship.order_item_name
        ELSE addr.shipping_address_1
    END AS shipping_address_1,
    addr.shipping_city,
    addr.billing_phone,
    price.cake_price,
    shipping_price.total_shipping
FROM wp_woocommerce_order_items ship
LEFT JOIN (
    SELECT
        post_id,
        MAX(CASE WHEN meta_key = '_shipping_address_1' THEN meta_value END) AS shipping_address_1,
        MAX(CASE WHEN meta_key = '_shipping_city' THEN meta_value END) AS shipping_city,
        MAX(CASE WHEN meta_key = '_billing_phone' THEN meta_value END) AS billing_phone
    FROM wp_postmeta
    GROUP BY post_id
) addr ON addr.post_id = ship.order_id
LEFT JOIN (
    SELECT
        post_id,
        MAX(CASE WHEN meta_key = '_order_total' THEN meta_value END)
        - MAX(CASE WHEN meta_key = '_order_shipping' THEN meta_value END)
        AS cake_price
    FROM wp_postmeta
    GROUP BY post_id
) price ON price.post_id = ship.order_id
LEFT JOIN (
    SELECT
        post_id,
        SUM(meta_value) AS total_shipping
    FROM wp_postmeta
    WHERE meta_key IN ('_order_shipping', '_order_shipping_tax')
    GROUP BY post_id
) shipping_price ON shipping_price.post_id = ship.order_id
WHERE
    ship.order_item_type = 'shipping'
    AND ship.order_id = :order_id;
"""

GET_ORDER_FULL = """
SELECT o.order_id AS post_id,   
    -- PRODUCTS
    COALESCE((
        SELECT JSON_ARRAYAGG(
            JSON_OBJECT(
                'order_item_id', pd.order_item_id,
                'product_name', pd.product_name,
                'quantity', pd.quantity,
                'pa_topper', pd.pa_topper,
                'pa_swieczka_nr_1', pd.pa_swieczka_nr_1,
                'pa_swieczka_nr_2', pd.pa_swieczka_nr_2,
                'warstwa_1', pd.warstwa_1,
                'warstwa_2', pd.warstwa_2,
                'warstwa_3', pd.warstwa_3,
                'warstwa_4', pd.warstwa_4,
                'dekoracja', pd.dekoracja,
                'smak', pd.smak
            )
        )
        FROM (
            SELECT
                woi.order_item_id,
                woi.order_item_name AS product_name,
                MAX(CASE WHEN wim.meta_key = '_qty' THEN wim.meta_value END) AS quantity,
                MAX(CASE WHEN wim.meta_key = 'pa_topper' THEN wim.meta_value END) AS pa_topper,
                MAX(CASE WHEN wim.meta_key = 'pa_swieczka-nr-1' THEN wim.meta_value END) AS pa_swieczka_nr_1,
                MAX(CASE WHEN wim.meta_key = 'pa_swieczka-nr-2' THEN wim.meta_value END) AS pa_swieczka_nr_2,
                MAX(CASE WHEN wim.meta_key = 'warstwa-1-najnizsza-warstwa' THEN wim.meta_value END) AS warstwa_1,
                MAX(CASE WHEN wim.meta_key = 'warstwa-2-srodkowa' THEN wim.meta_value END) AS warstwa_2,
                MAX(CASE WHEN wim.meta_key = 'warstwa-3-srodkowa' THEN wim.meta_value END) AS warstwa_3,
                MAX(CASE WHEN wim.meta_key = 'warstwa-4-zewnetrzna-warstwa' THEN wim.meta_value END) AS warstwa_4,
                MAX(CASE WHEN wim.meta_key = 'dekoracja' THEN wim.meta_value END) AS dekoracja,
                MAX(CASE WHEN wim.meta_key = 'smak' THEN wim.meta_value END) AS smak
            FROM wp_woocommerce_order_items woi
            JOIN wp_woocommerce_order_itemmeta wim ON wim.order_item_id = woi.order_item_id
            WHERE woi.order_id = :order_id
                AND woi.order_item_type = 'line_item'
                AND wim.meta_key IN (
                    '_qty', 'pa_topper', 'pa_swieczka-nr-1', 'pa_swieczka-nr-2',
                    'warstwa-1-najnizsza-warstwa', 'warstwa-2-srodkowa',
                    'warstwa-3-srodkowa', 'warstwa-4-zewnetrzna-warstwa',
                    'dekoracja', 'smak'
                )
            GROUP BY woi.order_item_id, woi.order_item_name
        ) pd
    ), JSON_ARRAY()) AS products,

    -- SHIPMENT DETAILS
    JSON_OBJECT(
        'order_id', :order_id,
        'shipping_address_1',
            CASE
                WHEN sm.order_item_name LIKE '%odbiór%' THEN sm.order_item_name
                ELSE smt.shipping_address_1
            END,
        'shipping_address_2', smt.shipping_address_2,
        'shipping_city', smt.shipping_city,
        'shipping_company', smt.shipping_company,
        'billing_phone', smt.billing_phone,
        'delivery_hour', smt.delivery_hour,
        'cake_price', COALESCE(pr.cake_price, 0),
        'total_shipping', COALESCE(pr.total_shipping, 0),
        'termobox_price', COALESCE(f.termobox_price, 0)
    ) AS shipment_details

FROM (SELECT :order_id AS order_id) o

-- SHIPPING META
LEFT JOIN (
    SELECT
        post_id,
        MAX(CASE WHEN meta_key = '_shipping_address_1' THEN meta_value END) AS shipping_address_1,
        MAX(CASE WHEN meta_key = '_shipping_address_2' THEN meta_value END) AS shipping_address_2,
        MAX(CASE WHEN meta_key = '_shipping_city' THEN meta_value END) AS shipping_city,
        MAX(CASE WHEN meta_key = '_shipping_company' THEN meta_value END) AS shipping_company,
        MAX(CASE WHEN meta_key = '_billing_phone' THEN meta_value END) AS billing_phone,
        MAX(CASE WHEN meta_key = 'Czas dostawy' THEN meta_value END) AS delivery_hour
    FROM wp_postmeta
    WHERE post_id = :order_id
    GROUP BY post_id
) smt ON smt.post_id = o.order_id

-- PRICES
LEFT JOIN (
    SELECT
        post_id,
        MAX(CASE WHEN meta_key = '_order_total' THEN meta_value END)
        - COALESCE(MAX(CASE WHEN meta_key = '_order_shipping' THEN meta_value END), 0)
        - COALESCE(MAX(CASE WHEN meta_key = '_order_shipping_tax' THEN meta_value END), 0)
        AS cake_price,
        COALESCE(SUM(CASE WHEN meta_key IN ('_order_shipping', '_order_shipping_tax') THEN meta_value END), 0)
        AS total_shipping
    FROM wp_postmeta
    WHERE post_id = :order_id
    GROUP BY post_id
) pr ON pr.post_id = o.order_id

-- FEES
LEFT JOIN (
    SELECT
        oi.order_id,
        COALESCE(SUM(oim.meta_value), 0) AS termobox_price
    FROM wp_woocommerce_order_items oi
    JOIN wp_woocommerce_order_itemmeta oim
        ON oi.order_item_id = oim.order_item_id
        AND oim.meta_key IN ('_line_total', '_line_tax')
    WHERE oi.order_item_type = 'fee'
        AND oi.order_id = :order_id
    GROUP BY oi.order_id
) f ON f.order_id = o.order_id

-- SHIPPING METHOD
LEFT JOIN (
    SELECT
        order_id,
        order_item_name
    FROM wp_woocommerce_order_items
    WHERE order_item_type = 'shipping'
        AND order_id = :order_id
) sm ON sm.order_id = o.order_id;
"""

