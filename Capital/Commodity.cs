namespace Capital;

/// <summary>
/// 商品类
///
/// 商品是用于交换的劳动产品，具有二重性：
/// 1. 使用价值：商品的有用性，满足人们的某种需要
/// 2. 价值：凝结在商品中的抽象劳动，决定了交换价值
///
/// 商品的两个基本属性：
/// - 有用性（自然属性）：不同商品有不同用途
/// - 价值（社会属性）：所有商品价值的本质是相同的，可以互相比较
/// </summary>
public class Commodity : Product
{
    /// <summary>
    /// 交换价值
    /// 一种商品与另一种商品交换的比例关系
    /// 例如：1把斧头 = 20斤小麦，这里的"20斤小麦"就是交换价值
    ///
    /// 交换价值与价值的关系：
    /// - 价值是交换价值的内容和基础
    /// - 交换价值是价值的表现形式
    /// </summary>
    /// <param name="commodity">要交换的目标商品</param>
    /// <returns>交换比例的描述</returns>
    public string Exchange(Commodity commodity)
    {
        // TODO: 实现具体的交换价值计算
        // 理论上：商品A的交换价值 = 商品A的价值 / 商品B的价值
        return ("可以交换多少个");
    }

    /// <summary>
    /// 私有字段：存储价值量
    /// </summary>
    private LaborTime _value;

    /// <summary>
    /// 私有字段：存储劳动对象
    /// </summary>
    private Labor _labor = null!;

    /// <summary>
    /// 私有字段：标记价值是否被直接设定
    /// 用于处理价值设定和劳动赋值之间的同步关系
    /// </summary>
    private bool _valueSetDirectly;

    /// <summary>
    /// 价值（ LaborTime 类型）
    ///
    /// 价值是凝结在商品中的抽象劳动时间。
    /// 价值量由生产该商品所需的社会必要劳动时间决定。
    ///
    /// 赋值逻辑：
    /// - 如果直接设定Value，则反向推导抽象劳动时间
    /// - 如果设定Labor，则自动从劳动的抽象劳动获取价值
    /// </summary>
    public LaborTime Value
    {
        get => _value;
        set
        {
            _value = value;
            _valueSetDirectly = true;  // 标记为直接设定
            _labor.AbstractLabor = value;  // 反向推导抽象劳动
        }
    }

    /// <summary>
    /// 生产该商品所需的劳动（隐藏父类的同名属性）
    ///
    /// 父类Product的Labor是可选的，但商品必须有关联劳动，
    /// 因为商品的价值来源于劳动。
    ///
    /// 赋值逻辑：
    /// - 如果价值不是直接设定的，则从抽象劳动获取价值
    /// - 这样保证了价值和劳动的同步
    /// </summary>
    public new required Labor Labor
    {
        get => _labor;
        set
        {
            _labor = value;
            // 如果价值不是直接设定的，则从抽象劳动获取
            if (!_valueSetDirectly)
            {
                _value = _labor.AbstractLabor;
            }
        }
    }
}
