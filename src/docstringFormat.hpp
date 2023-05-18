//
// Created by felix on 20.04.23.
//

#ifndef SRC_DOCSTRINGFORMAT_HPP
#define SRC_DOCSTRINGFORMAT_HPP


#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

const std::string PY_TAB = "    ";

enum class ParameterKind
{
    ARG,
    POS_ONLY,
    KW_ONLY,
    VARIADIC_ARG,
    KEYWORD_ARG,
};

std::ostream& operator<<(std::ostream &out, ParameterKind const &obj) noexcept
{
    switch (obj)
    {
        case ParameterKind::ARG:
            return out << "Argument";
        case ParameterKind::POS_ONLY:
            return out << "Positional only argument";
        case ParameterKind::KW_ONLY:
            return out << "Keyword only argument";
        case ParameterKind::VARIADIC_ARG:
            return out << "Variadic arguments";
        case ParameterKind::KEYWORD_ARG:
            return out << "Keyword arguments";
    }
    
    return out;
}

struct FunctionParameter
{
    std::string name;
    std::string default_value;
    std::string type;
    ParameterKind kind;
    uint line_no;
    std::string description;
    
    void py_print();
};

struct FunctionReturn
{
    std::string type;
    uint line_no;
    std::string description;
};

struct FunctionDocstring
{
    std::string docstring;
    uint start_line;
    uint end_line;
};

struct FunctionInfo
{
    uint offset;
    std::string name;
    FunctionDocstring docstring;
    FunctionReturn returns;
    std::vector<FunctionParameter> args {};
    
    int get_file_write_position()
    {
        if (!docstring.docstring.empty())
        {
            return docstring.start_line;
        }
        
        if (returns.line_no > 0)
        {
            return static_cast<int>(returns.line_no + 1);
        }
        else if (!args.empty())
        {
            return static_cast<int>(args[args.size() - 1].line_no + 1);
        }
        
        return 0;
    }
};

struct DocstringFormat
{
    FunctionInfo functionInfo;
    
    virtual std::string docstringArgs() = 0;
    virtual std::string docstringReturn() = 0;
    
    std::string get_tabs()
    {
        auto current_py_tab = PY_TAB;
        for (uint idx = 0; idx < (functionInfo.offset / 4); ++idx)
        {
            current_py_tab += PY_TAB;
        }
        
        return current_py_tab;
    }
};

struct GoogleDocstring : DocstringFormat
{
    std::string docstringArgs() override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
    
        if (functionInfo.docstring.docstring.empty())
        {
            sstream << PY_TAB << "\"\"\"\n";
        }
        else
        {
            sstream << PY_TAB << "\"\"\"";
            sstream << functionInfo.docstring.docstring;
            sstream << "\n";
        }
        
        if (PY_TAB != current_py_tab)
        {
            sstream << PY_TAB;
        }
        else
        {
            sstream << PY_TAB;
            current_py_tab = PY_TAB + PY_TAB;
        }
        
        sstream << "Args:\n";
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                      [&sstream, &current_py_tab](const FunctionParameter &val){
            sstream << current_py_tab << val.name;
            if (!val.type.empty())
            {
                sstream << " (" << val.type << ")";
            }
            
            if (val.description.empty())
            {
                sstream << " : " << val.kind << "\n";
            }
            else
            {
                sstream << " : " << val.kind  << ". " << val.description << "\n";
            }
            
            if (!val.default_value.empty())
            {
                sstream << current_py_tab << PY_TAB << "(default is " << val.default_value << ")\n";
            }
        });
        
        sstream << PY_TAB << "\"\"\"\n";
        return sstream.str();
    }
    
    std::string docstringReturn() override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
    
        if (PY_TAB != current_py_tab)
        {
            sstream << PY_TAB;
        }
        
        if (!functionInfo.returns.description.empty() || !functionInfo.returns.type.empty())
        {
            sstream << "Returns:\n";
            sstream << current_py_tab;
            if (!functionInfo.returns.type.empty())
            {
                sstream << "( " << functionInfo.returns.type << " ) : ";
            }
            sstream << functionInfo.returns.description << "\n";
        }
        
        return sstream.str();
    }
};

struct reStructuredDocstring : DocstringFormat
{
    std::string docstringArgs() override
    {
        std::stringstream sstream;
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                      [&sstream](const FunctionParameter &val){
                         
                         sstream << ":param " << val.name << ": (" << val.kind << ")";
                         
                         if (!val.description.empty())
                         {
                             sstream << " " << val.description;
                         }
                         
                         sstream << "\n";
                         
                         if (!val.type.empty())
                         {
                             sstream << ":type " << val.name << ": " << val.type << ")" << "\n";
                         }
                         if (!val.default_value.empty())
                         {
                             sstream << "(default is " << val.default_value << ")\n";
                         }
                      });
        
        return sstream.str();
    }
    
    std::string docstringReturn() override
    {
        std::stringstream sstream;
        sstream << ":returns:" << functionInfo.returns.description << "\n";
        sstream << ":returns:\n";
        if (!functionInfo.returns.type.empty())
        {
            sstream << ":rtype:" << functionInfo.returns.type << "\n";
        }
        return sstream.str();
    }
};

struct NumpyDocstring : DocstringFormat
{
    std::string docstringArgs() override
    {
        std::stringstream sstream;
        sstream << "Parameters\n";
        sstream << "----------\n";
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                      [&sstream](const FunctionParameter &val){
            
                          sstream << val.name;
            
                          if (!val.type.empty())
                          {
                              sstream << " : " << val.type;
                              
                              if (!val.default_value.empty())
                              {
                                  sstream << ", optional";
                              }
                          }
    
                          sstream << "\n";
                          sstream << PY_TAB << val.description;
    
                          if (!val.default_value.empty())
                          {
                              sstream << "(default is " << val.default_value << ")";
                          }
    
                          sstream << "\n";
                      });
        
        return sstream.str();
    }
    
    std::string docstringReturn() override
    {
        std::stringstream sstream;
        
        sstream << "Returns\n";
        sstream << "-------\n";
//        sstream << returnText.name;
    
        if (!functionInfo.returns.type.empty())
        {
            sstream << " : " << functionInfo.returns.type;
        
            if (!functionInfo.returns.type.empty())
            {
                sstream << ", optional";
            }
        }
    
        sstream << "\n";
        sstream << PY_TAB << functionInfo.returns.description << "\n";
        
        return sstream.str();
    }
};

#endif //SRC_DOCSTRINGFORMAT_HPP
