namespace Capital;

/// <summary>
/// 产品类
///
/// 产品与商品的区别：
/// - 产品（Product）：只有使用价值，用于满足生产者自身需要
/// - 商品（Commodity）：既有使用价值，又有交换价值，用于交换
///
/// 原始社会的产品还不是商品，因为它们不用于交换。
/// 只有当产品进入交换过程，成为交换的对象时，才成为商品。
/// </summary>
public class Product
{
    /// <summary>
    /// 产品名称
    /// </summary>
    public required string Name { get; set; }

    /// <summary>
    /// 使用价值
    /// 返回产品本身，因为产品的使用价值就是产品自身
    /// 这是政治经济学的观点：商品首先必须是一个有用物
    /// </summary>
    public Product UseValue
    {
        get { return this; }
    }

    /// <summary>
    /// 有用性（描述使用价值的具体形式）
    /// 例如："食物"、"工具"、"衣服"等
    /// 反映产品的自然属性
    /// </summary>
    public required string Usefulness { get; set; }

    /// <summary>
    /// 生产该产品所需的劳动
    /// 对于原始社会的产品，这个属性可选（可能有无劳动的自然产物）
    /// 对于商品，这个属性是必需的
    /// </summary>
    public Labor? Labor { get; set; }
}
