//
// Created by felix on 20.04.23.
//

#ifndef SRC_DOCSTRINGFORMAT_HPP
#define SRC_DOCSTRINGFORMAT_HPP


#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <iostream>

const std::string PY_TAB = "    ";

auto replaceAll = [](std::string& str_, const std::string& original, const std::string& new_){
    while(str_.find(original) != std::string::npos)
    {
        str_.replace(str_.find(original), original.size(), new_);
    }
};

enum class ParameterKind
{
    ARG,
    POS_ONLY,
    KW_ONLY,
    VARIADIC_ARG,
    KEYWORD_ARG,
};

ParameterKind from_str(const std::string &kind)
{
    if (kind == "Argument")
    {
        return ParameterKind::ARG;
    }
    else if (kind == "Positional only argument")
    {
        return ParameterKind::POS_ONLY;
    }
    else if (kind == "Keyword only argument")
    {
        return ParameterKind::KW_ONLY;
    }
    else if (kind == "Variadic arguments")
    {
        return ParameterKind::VARIADIC_ARG;
    }
    else if (kind == "Keyword arguments")
    {
        return ParameterKind::KEYWORD_ARG;
    }
    
    return ParameterKind::ARG;
}

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
    
    [[ nodiscard ]] std::string to_json(const uint index) noexcept
    {
        std::stringstream sstream;
    
        sstream << "{";
        sstream << "\"index\":" << "\"" << index << "\",";
        sstream << "\"name\":" << "\"" << name << "\",";
        sstream << "\"default_value\":" << "\"" << default_value << "\",";
        sstream << "\"type\":" << "\"" << type << "\",";
        sstream << "\"kind\":" << "\"" << kind << "\",";
        sstream << "\"line_no\":" << "\"" << line_no << "\",";
        sstream << "\"description\":" << "\"" << description << "\"";
        sstream << "}";
        
        return sstream.str();
    }
};

struct FunctionReturn
{
    std::string type;
    uint line_no;
    std::string description;
    
    [[ nodiscard ]] std::string to_json() noexcept
    {
        std::stringstream sstream;
    
        sstream << "\"return\":{";
        sstream << "\"type\":" << "\"" << type << "\",";
        sstream << "\"line_no\":" << "\"" << line_no << "\",";
        sstream << "\"description\":" << "\"" << description << "\"";
        sstream << "}";
    
        return sstream.str();
    }
};

struct FunctionDocstring
{
    std::string docstring;
    uint start_line;
    uint end_line;
    
    [[ nodiscard ]] std::string to_json() noexcept
    {
        std::string docstring_ = docstring;
        std::stringstream sstream;
        
        replaceAll(docstring_, "\n", "");
    
        sstream << "\"docstring\":{";
        sstream << "\"docstring\":" << "\"" << docstring_ << "\",";
        sstream << "\"start_line\":" << "\"" << start_line << "\",";
        sstream << "\"end_line\":" << "\"" << end_line << "\"";
        sstream << "}";
    
        return sstream.str();
    }
};

struct FunctionInfo
{
    uint offset;
    std::string name;
    FunctionDocstring docstring;
    FunctionReturn returns;
    std::vector<FunctionParameter> args {};
    
    [[ nodiscard ]] std::string to_json() noexcept
    {
        std::stringstream sstream;
        
        sstream << "{\"function_args\": [";
        
        uint counter = 0;
        size_t args_size = args.size() - 1;
        
        std::for_each(args.begin(), args.end(),
                      [&sstream, &counter, &args_size](FunctionParameter &val){
            sstream << val.to_json(counter);
            
            if (counter < args_size)
            {
                sstream << ",";
            }
            
            ++counter;
        });
        sstream << "],";
        sstream << returns.to_json();
        sstream << ",";
        sstream << docstring.to_json();
        sstream << "}";
        
        return sstream.str();
    }
    
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
    
    virtual std::string docstringArgs() noexcept = 0;
    virtual std::string docstringReturn() noexcept = 0;
    
    virtual void check_current_docstring() noexcept = 0;
    
    [[ nodiscard ]] std::string docstring() noexcept
    {
        std::stringstream sstream;
        auto current_pytab = get_tabs();
    
        sstream << current_pytab << R"(""")";
        if (functionInfo.docstring.docstring.empty())
        {
            sstream << "\n";
        }
        sstream << docstringArgs();
        sstream << docstringReturn();
        
        sstream << current_pytab << R"(""")";
        if (functionInfo.docstring.docstring.empty())
        {
            sstream << "\n";
        }
        
        return sstream.str();
    }
    
    [[ nodiscard ]] std::string get_tabs() noexcept
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
    void check_current_docstring() noexcept override
    {
        auto current_py_tab = get_tabs();
        auto google_args_begin = functionInfo.docstring.docstring.find("Args:");
        
        if (google_args_begin < std::string::npos)
        {
            functionInfo.docstring.docstring = functionInfo.docstring.docstring.substr(0, google_args_begin - (current_py_tab.size() + 1));
            functionInfo.docstring.end_line = functionInfo.docstring.start_line + google_args_begin;
        }
    }
    
    std::string docstringArgs() noexcept override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
        
        if (!functionInfo.docstring.docstring.empty())
        {
            sstream << functionInfo.docstring.docstring;
            sstream << "\n";
        }
        
        if (PY_TAB != current_py_tab)
        {
            sstream << current_py_tab;
            current_py_tab += PY_TAB;
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
        
        return sstream.str();
    }
    
    std::string docstringReturn() noexcept override
    {
        std::stringstream sstream;
        auto current_py_tab = get_tabs();
        
        sstream << "\n";
        
        if (!functionInfo.returns.description.empty() || !functionInfo.returns.type.empty())
        {
            if (PY_TAB != current_py_tab)
            {
                sstream << PY_TAB;
            }
            else
            {
                sstream << PY_TAB;
                current_py_tab = PY_TAB + PY_TAB;
            }
            
            sstream << "Returns:\n";
            sstream << current_py_tab;
            if (!functionInfo.returns.type.empty())
            {
                sstream << "( " << functionInfo.returns.type << " ) : ";
            }
            sstream << functionInfo.returns.description << "\n";
    
            sstream << "\n";
        }
        
        return sstream.str();
    }
};

struct reStructuredDocstring : DocstringFormat
{
    void check_current_docstring() noexcept override {}
    
    std::string docstringArgs() noexcept override
    {
        std::stringstream sstream;
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                    [&sstream](const FunctionParameter &val)
        {
         
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
    
    std::string docstringReturn() noexcept override
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
    void check_current_docstring() noexcept override {}
    
    std::string docstringArgs() noexcept override
    {
        std::stringstream sstream;
        sstream << "Parameters\n";
        sstream << "----------\n";
        std::for_each(functionInfo.args.begin(), functionInfo.args.end(),
                      [&sstream](const FunctionParameter &val)
        {
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
    
    std::string docstringReturn() noexcept override
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
