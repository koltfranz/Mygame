namespace Capital;

public enum Gender
{
    Male,
    Female
};

public class Person
{
    public string Name { get; set; }
    public int Age { get; set; }
    public Gender Gender { get; set; }
    public void Labor()
    {
        //TODO: 添加具体劳动逻辑
    }
    public void Eat()
    {
        //TODO: 添加具体吃东西逻辑
    }
    public double Satiation  { get; set; }

    public double Health { get; set; }
    public Person(string name, int age, Gender gender)
    {
        Name = name;
        Age = age;
        Gender = gender;
    }
}